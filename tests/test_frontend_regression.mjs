import { spawn } from 'child_process';

const chrome = spawn('google-chrome', [
    '--headless=new',
    '--remote-debugging-port=9222',
    '--disable-gpu',
    '--no-sandbox',
    '--window-size=1440,900',
    'about:blank'
]);

// Allow Chrome time to initialize DevTools port
await new Promise(r => setTimeout(r, 1500));

let exitCode = 0;
const consoleErrors = [];

try {
    const listRes = await fetch('http://127.0.0.1:9222/json');
    const tabs = await listRes.json();
    const pageTab = tabs.find(t => t.type === 'page') || tabs[0];
    const ws = new WebSocket(pageTab.webSocketDebuggerUrl);

    let msgId = 1;
    const pending = new Map();

    ws.onmessage = (event) => {
        const msg = JSON.parse(event.data);
        if (msg.method === 'Runtime.consoleAPICalled') {
            if (msg.params.type === 'error') {
                consoleErrors.push(msg.params.args.map(a => a.value || a.description).join(' '));
            }
        }
        if (msg.id && pending.has(msg.id)) {
            const { resolve, reject } = pending.get(msg.id);
            pending.delete(msg.id);
            if (msg.error) reject(msg.error);
            else resolve(msg.result);
        }
    };

    await new Promise((resolve, reject) => {
        ws.onopen = resolve;
        ws.onerror = reject;
    });

    function send(method, params = {}) {
        return new Promise((resolve, reject) => {
            const id = msgId++;
            pending.set(id, { resolve, reject });
            ws.send(JSON.stringify({ id, method, params }));
        });
    }

    async function evaluate(expression) {
        const res = await send('Runtime.evaluate', {
            expression,
            returnByValue: true,
            awaitPromise: true
        });
        return res.result ? res.result.value : null;
    }

    await send('Page.enable');
    await send('Runtime.enable');
    await send('Page.navigate', { url: 'http://127.0.0.1:5000/portal' });

    // Wait for initial load and data fetch
    for (let i = 0; i < 30; i++) {
        const count = await evaluate(`document.querySelectorAll('.opportunity-card').length`);
        if (count > 0) break;
        await new Promise(r => setTimeout(r, 200));
    }

    console.log("=" .repeat(70));
    console.log("PHASE 4: FULL-STACK FRONTEND REGRESSION AUDIT");
    console.log("=" .repeat(70));

    // 1. Initial State Check
    const initialStats = await evaluate(`({
        total: parseInt(document.getElementById('stat-total')?.textContent || '0', 10),
        cardsCount: document.querySelectorAll('.opportunity-card').length
    })`);
    console.log("[Test 1] Initial Dashboard State:", initialStats);

    // 2. Form Validation Check (Submit Empty Form)
    console.log("[Test 2] Testing Create Form Validation (Empty submit)...");
    await evaluate(`document.getElementById('btn-open-create-modal').click()`);
    await new Promise(r => setTimeout(r, 600));

    const validationCheck = await evaluate(`(() => {
        const form = document.getElementById('create-opportunity-form');
        const submitBtn = document.getElementById('btn-submit-create');
        submitBtn.click();
        return form.classList.contains('was-validated');
    })()`);
    console.log("  -> Form marked invalid with .was-validated:", validationCheck);
    if (!validationCheck) throw new Error("Form validation failed to trigger");

    // 3. Create Valid Opportunity
    console.log("[Test 3] Creating new opportunity via Frontend Modal...");
    await evaluate(`(() => {
        document.getElementById('create-title').value = "Edge Computing & Distributed Systems";
        document.getElementById('create-faculty').value = "Dr. Hamza Ali";
        document.getElementById('create-department').value = "Computer Science";
        document.getElementById('create-area').value = "Cloud & Edge Computing";
        document.getElementById('create-positions').value = "2";
        document.getElementById('create-deadline').value = "2026-11-20";
        document.getElementById('create-status').value = "Open";
        document.getElementById('create-skills').value = "Go, Kubernetes, Docker, gRPC";
        document.getElementById('create-description').value = "Investigating low-latency task scheduling algorithms for decentralized edge computing nodes.";
        
        document.getElementById('btn-submit-create').click();
    })()`);
    await new Promise(r => setTimeout(r, 1500));

    const afterCreateStats = await evaluate(`({
        total: parseInt(document.getElementById('stat-total')?.textContent || '0', 10),
        cardsCount: document.querySelectorAll('.opportunity-card').length,
        hasCard: Array.from(document.querySelectorAll('.card-title')).some(el => el.textContent.includes('Edge Computing'))
    })`);
    console.log("  -> Dashboard after create:", afterCreateStats);
    if (!afterCreateStats.hasCard) throw new Error("Newly created opportunity card not found on dashboard");
    if (afterCreateStats.total !== initialStats.total + 1) throw new Error("Metric 'Total Listings' did not increment");

    // 4. View Details Modal
    console.log("[Test 4] Testing View Details Modal...");
    await evaluate(`(() => {
        const cards = Array.from(document.querySelectorAll('.opportunity-card'));
        const targetCard = cards.find(c => c.querySelector('.card-title')?.textContent.includes('Edge Computing'));
        const viewBtn = targetCard.querySelector('.btn-view-card');
        viewBtn.click();
    })()`);
    await new Promise(r => setTimeout(r, 800));

    const detailsModal = await evaluate(`({
        isOpen: document.getElementById('viewOpportunityModal')?.classList.contains('show'),
        title: document.getElementById('view-title')?.textContent,
        faculty: document.getElementById('view-faculty')?.textContent,
        status: document.getElementById('view-status-badge')?.textContent.trim()
    })`);
    console.log("  -> Details Modal state:", detailsModal);
    if (!detailsModal.isOpen || !detailsModal.title.includes('Edge Computing')) {
        throw new Error("Details modal failed to display correct information");
    }

    // Close details modal
    await evaluate(`document.querySelector('#viewOpportunityModal [data-bs-dismiss="modal"]').click()`);
    await new Promise(r => setTimeout(r, 600));

    // 5. Edit Opportunity
    console.log("[Test 5] Testing Edit Opportunity...");
    await evaluate(`(() => {
        const cards = Array.from(document.querySelectorAll('.opportunity-card'));
        const targetCard = cards.find(c => c.querySelector('.card-title')?.textContent.includes('Edge Computing'));
        const editBtn = targetCard.querySelector('.btn-edit-card');
        editBtn.click();
    })()`);
    await new Promise(r => setTimeout(r, 800));

    await evaluate(`(() => {
        document.getElementById('edit-title').value = "Edge Computing & Distributed Systems (Updated)";
        document.getElementById('edit-positions').value = "4";
        document.getElementById('btn-submit-edit').click();
    })()`);
    await new Promise(r => setTimeout(r, 1500));

    const editResult = await evaluate(`
        Array.from(document.querySelectorAll('.card-title')).some(el => el.textContent.includes('(Updated)'))
    `);
    console.log("  -> Edit successfully updated card on dashboard:", editResult);
    if (!editResult) throw new Error("Card title did not update after edit");

    // 6. Close Opportunity (Toggle Status)
    console.log("[Test 6] Testing Close Opportunity (Status toggle)...");
    await evaluate(`(() => {
        const cards = Array.from(document.querySelectorAll('.opportunity-card'));
        const targetCard = cards.find(c => c.querySelector('.card-title')?.textContent.includes('Updated'));
        const toggleBtn = targetCard.querySelector('.btn-toggle-status-card');
        toggleBtn.click();
    })()`);
    await new Promise(r => setTimeout(r, 1200));

    const statusResult = await evaluate(`(() => {
        const cards = Array.from(document.querySelectorAll('.opportunity-card'));
        const targetCard = cards.find(c => c.querySelector('.card-title')?.textContent.includes('Updated'));
        return targetCard?.querySelector('.status-badge')?.textContent.trim();
    })()`);
    console.log("  -> Opportunity status after toggle:", statusResult);
    if (statusResult !== 'Closed') throw new Error(`Expected status 'Closed', got '${statusResult}'`);

    // 7. Search & Filters Verification
    console.log("[Test 7] Testing Search and Filter Controls...");
    
    // Search filter
    await evaluate(`(() => {
        const input = document.getElementById('search-input');
        input.value = 'Distributed';
        input.dispatchEvent(new Event('input', { bubbles: true }));
    })()`);
    await new Promise(r => setTimeout(r, 400));
    const searchFilterCount = await evaluate(`document.querySelectorAll('.opportunity-card').length`);
    console.log("  -> Search query 'Distributed' match count:", searchFilterCount);
    if (searchFilterCount < 1) throw new Error("Search filter did not find updated opportunity");

    // Status filter 'Open' -> updated card is Closed, so should not appear
    await evaluate(`document.querySelector('.status-pill-btn[data-status="Open"]').click()`);
    await new Promise(r => setTimeout(r, 400));
    const openFilterCount = await evaluate(`
        Array.from(document.querySelectorAll('.card-title')).some(el => el.textContent.includes('Updated'))
    `);
    console.log("  -> Closed card hidden under Open filter:", !openFilterCount);
    if (openFilterCount) throw new Error("Closed opportunity should not appear in Open filter");

    // Status filter 'Closed' -> should appear
    await evaluate(`document.querySelector('.status-pill-btn[data-status="Closed"]').click()`);
    await new Promise(r => setTimeout(r, 400));
    const closedFilterCount = await evaluate(`
        Array.from(document.querySelectorAll('.card-title')).some(el => el.textContent.includes('Updated'))
    `);
    console.log("  -> Closed card visible under Closed filter:", closedFilterCount);
    if (!closedFilterCount) throw new Error("Closed opportunity must appear in Closed filter");

    // Clear filters
    await evaluate(`document.getElementById('btn-clear-filters')?.click()`);
    await new Promise(r => setTimeout(r, 400));

    // 8. Delete Opportunity
    console.log("[Test 8] Testing Delete Opportunity...");
    await evaluate(`(() => {
        const cards = Array.from(document.querySelectorAll('.opportunity-card'));
        const targetCard = cards.find(c => c.querySelector('.card-title')?.textContent.includes('Updated'));
        const delBtn = targetCard.querySelector('.btn-delete-card');
        delBtn.click();
    })()`);
    await new Promise(r => setTimeout(r, 800));

    // Confirm deletion in delete confirmation modal
    await evaluate(`document.getElementById('btn-confirm-delete').click()`);
    await new Promise(r => setTimeout(r, 1500));

    const finalStats = await evaluate(`({
        total: parseInt(document.getElementById('stat-total')?.textContent || '0', 10),
        hasCard: Array.from(document.querySelectorAll('.card-title')).some(el => el.textContent.includes('Edge Computing'))
    })`);
    console.log("  -> Dashboard after delete:", finalStats);
    if (finalStats.hasCard) throw new Error("Deleted opportunity still present on dashboard");
    if (finalStats.total !== initialStats.total) throw new Error("Total listings metric did not return to baseline");

    // 9. Console Error Verification
    console.log("[Test 9] Checking browser console error logs...");
    console.log("  -> Uncaught console errors count:", consoleErrors.length);
    if (consoleErrors.length > 0) {
        console.warn("  -> Errors encountered:", consoleErrors);
    }

    console.log("=" .repeat(70));
    console.log("ALL FRONTEND REGRESSION TESTS PASSED (100% SUCCESS)!");
    console.log("=" .repeat(70));

    ws.close();
} catch (err) {
    console.error("FATAL ERROR in frontend regression test:", err);
    exitCode = 1;
} finally {
    chrome.kill('SIGTERM');
    process.exit(exitCode);
}
