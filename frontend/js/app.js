/**
 * University Research Opportunity Portal - Academic SaaS Application Logic
 * Integrates with Flask RESTful API (/api/opportunities) for full CRUD operations.
 */

// API Base URL Detection (works whether served via Flask or standalone)
const API_BASE_URL = window.location.origin.startsWith('http')
    ? `${window.location.origin}/api`
    : 'http://127.0.0.1:5000/api';

// Application State
const state = {
    opportunities: [],
    filteredOpportunities: [],
    searchQuery: '',
    departmentFilter: '',
    areaFilter: '',
    statusFilter: 'all', // 'all', 'Open', 'Closed'
    sortBy: 'newest', // 'newest', 'deadline', 'positions'
    activeDeleteId: null,
    activeEditId: null,
    activeViewId: null
};

// Bootstrap Modal Instances
let createModalInstance = null;
let editModalInstance = null;
let viewModalInstance = null;
let deleteModalInstance = null;

// ==============================================================================
// Initialization
// ==============================================================================
document.addEventListener('DOMContentLoaded', () => {
    initBootstrapModals();
    initEventListeners();
    fetchOpportunities().then(() => {
        handleUrlHash();
    });
    window.addEventListener('hashchange', handleUrlHash);
});

function handleUrlHash() {
    const hash = window.location.hash;
    if (hash === '#create' && createModalInstance) {
        createModalInstance.show();
    } else if (hash.startsWith('#details-') && viewModalInstance) {
        const id = parseInt(hash.replace('#details-', ''), 10);
        if (id) viewOpportunityDetails(id);
    } else if (hash.startsWith('#edit-') && editModalInstance) {
        const id = parseInt(hash.replace('#edit-', ''), 10);
        if (id) openEditModal(id);
    }
}

function initBootstrapModals() {
    const createModalEl = document.getElementById('createOpportunityModal');
    if (createModalEl) {
        createModalInstance = new bootstrap.Modal(createModalEl);
        createModalEl.addEventListener('hidden.bs.modal', () => {
            const form = document.getElementById('create-opportunity-form');
            if (form) {
                form.reset();
                form.classList.remove('was-validated');
            }
            const err = document.getElementById('create-form-error');
            if (err) err.classList.add('d-none');
        });
    }

    const editModalEl = document.getElementById('editOpportunityModal');
    if (editModalEl) {
        editModalInstance = new bootstrap.Modal(editModalEl);
        editModalEl.addEventListener('hidden.bs.modal', () => {
            const form = document.getElementById('edit-opportunity-form');
            if (form) {
                form.reset();
                form.classList.remove('was-validated');
            }
            const err = document.getElementById('edit-form-error');
            if (err) err.classList.add('d-none');
        });
    }

    const viewModalEl = document.getElementById('viewOpportunityModal');
    if (viewModalEl) viewModalInstance = new bootstrap.Modal(viewModalEl);

    const deleteModalEl = document.getElementById('deleteConfirmModal');
    if (deleteModalEl) deleteModalInstance = new bootstrap.Modal(deleteModalEl);
}

function initEventListeners() {
    // Search input (live filter)
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            state.searchQuery = e.target.value.trim().toLowerCase();
            applyFilters();
        });
    }

    // Department Filter
    const deptSelect = document.getElementById('filter-department');
    if (deptSelect) {
        deptSelect.addEventListener('change', (e) => {
            state.departmentFilter = e.target.value;
            applyFilters();
        });
    }

    // Area Filter
    const areaSelect = document.getElementById('filter-area');
    if (areaSelect) {
        areaSelect.addEventListener('change', (e) => {
            state.areaFilter = e.target.value;
            applyFilters();
        });
    }

    // Status Filter Segmented Buttons
    const statusBtns = document.querySelectorAll('.status-pill-btn');
    statusBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            statusBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            state.statusFilter = btn.getAttribute('data-status');
            applyFilters();
        });
    });

    // Sort By Selector
    const sortSelect = document.getElementById('sort-by');
    if (sortSelect) {
        sortSelect.addEventListener('change', (e) => {
            state.sortBy = e.target.value;
            applyFilters();
        });
    }

    // Clear Filters Button
    const clearBtn = document.getElementById('btn-clear-filters');
    if (clearBtn) {
        clearBtn.addEventListener('click', resetFilters);
    }

    // Refresh Data Button
    const refreshBtn = document.getElementById('btn-refresh-data');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', fetchOpportunities);
    }

    // Create Opportunity Form Submit
    const createForm = document.getElementById('create-opportunity-form');
    if (createForm) {
        createForm.addEventListener('submit', handleCreateSubmit);
    }

    // Edit Opportunity Form Submit
    const editForm = document.getElementById('edit-opportunity-form');
    if (editForm) {
        editForm.addEventListener('submit', handleEditSubmit);
    }

    // Delete Confirmation Button
    const confirmDeleteBtn = document.getElementById('btn-confirm-delete');
    if (confirmDeleteBtn) {
        confirmDeleteBtn.addEventListener('click', handleConfirmDelete);
    }

    // Detail Modal Quick Actions
    const viewEditBtn = document.getElementById('btn-view-edit');
    if (viewEditBtn) {
        viewEditBtn.addEventListener('click', () => {
            if (viewModalInstance) viewModalInstance.hide();
            if (state.activeViewId) openEditModal(state.activeViewId);
        });
    }

    const viewDeleteBtn = document.getElementById('btn-view-delete');
    if (viewDeleteBtn) {
        viewDeleteBtn.addEventListener('click', () => {
            if (viewModalInstance) viewModalInstance.hide();
            if (state.activeViewId) openDeleteModal(state.activeViewId);
        });
    }

    const viewToggleBtn = document.getElementById('btn-view-toggle-status');
    if (viewToggleBtn) {
        viewToggleBtn.addEventListener('click', () => {
            if (state.activeViewId) {
                const opp = state.opportunities.find(o => o.id === state.activeViewId);
                if (opp) {
                    toggleOpportunityStatus(opp.id, opp.status);
                    if (viewModalInstance) viewModalInstance.hide();
                }
            }
        });
    }
}

// ==============================================================================
// Data Fetching & State Updates
// ==============================================================================
async function fetchOpportunities() {
    setLoading(true);
    try {
        const response = await fetch(`${API_BASE_URL}/opportunities`);
        if (!response.ok) {
            throw new Error(`Server returned HTTP ${response.status}`);
        }
        const data = await response.json();
        state.opportunities = Array.isArray(data) ? data : [];
        
        updateMetrics();
        populateFilterDropdowns();
        applyFilters();
    } catch (error) {
        console.error('Failed to load opportunities:', error);
        showToast(`Failed to load data: ${error.message}`, 'danger');
        renderEmptyState(true, 'Failed to Connect to API', 'Ensure the Flask server is running at http://127.0.0.1:5000');
    } finally {
        setLoading(false);
    }
}

function updateMetrics() {
    const total = state.opportunities.length;
    const open = state.opportunities.filter(o => o.status === 'Open').length;
    const closed = state.opportunities.filter(o => o.status === 'Closed').length;
    const positions = state.opportunities.reduce((acc, o) => acc + (parseInt(o.available_positions, 10) || 0), 0);

    const totalEl = document.getElementById('stat-total');
    const openEl = document.getElementById('stat-open');
    const closedEl = document.getElementById('stat-closed');
    const positionsEl = document.getElementById('stat-positions');

    if (totalEl) totalEl.textContent = total;
    if (openEl) openEl.textContent = open;
    if (closedEl) closedEl.textContent = closed;
    if (positionsEl) positionsEl.textContent = positions;
}

function populateFilterDropdowns() {
    const deptSelect = document.getElementById('filter-department');
    const areaSelect = document.getElementById('filter-area');

    if (deptSelect) {
        const currentDept = state.departmentFilter;
        const uniqueDepts = Array.from(new Set(state.opportunities.map(o => o.department))).filter(Boolean).sort();
        deptSelect.innerHTML = '<option value="">All Departments</option>' +
            uniqueDepts.map(d => `<option value="${escapeHtml(d)}" ${d === currentDept ? 'selected' : ''}>${escapeHtml(d)}</option>`).join('');
    }

    if (areaSelect) {
        const currentArea = state.areaFilter;
        const uniqueAreas = Array.from(new Set(state.opportunities.map(o => o.research_area))).filter(Boolean).sort();
        areaSelect.innerHTML = '<option value="">All Areas</option>' +
            uniqueAreas.map(a => `<option value="${escapeHtml(a)}" ${a === currentArea ? 'selected' : ''}>${escapeHtml(a)}</option>`).join('');
    }
}

// ==============================================================================
// Filtering & Sorting
// ==============================================================================
function applyFilters() {
    let list = [...state.opportunities];

    // Status filter
    if (state.statusFilter !== 'all') {
        list = list.filter(o => o.status === state.statusFilter);
    }

    // Department filter
    if (state.departmentFilter) {
        list = list.filter(o => o.department === state.departmentFilter);
    }

    // Area filter
    if (state.areaFilter) {
        list = list.filter(o => o.research_area === state.areaFilter);
    }

    // Search query
    if (state.searchQuery) {
        const q = state.searchQuery;
        list = list.filter(o => 
            (o.title && o.title.toLowerCase().includes(q)) ||
            (o.faculty_name && o.faculty_name.toLowerCase().includes(q)) ||
            (o.department && o.department.toLowerCase().includes(q)) ||
            (o.research_area && o.research_area.toLowerCase().includes(q)) ||
            (o.required_skills && o.required_skills.toLowerCase().includes(q)) ||
            (o.description && o.description.toLowerCase().includes(q))
        );
    }

    // Sorting
    if (state.sortBy === 'deadline') {
        list.sort((a, b) => new Date(a.application_deadline) - new Date(b.application_deadline));
    } else if (state.sortBy === 'positions') {
        list.sort((a, b) => (b.available_positions || 0) - (a.available_positions || 0));
    } else {
        // Newest / default by ID descending
        list.sort((a, b) => b.id - a.id);
    }

    state.filteredOpportunities = list;
    renderOpportunityCards();
    updateFeedbackBar();
}

function resetFilters() {
    state.searchQuery = '';
    state.departmentFilter = '';
    state.areaFilter = '';
    state.statusFilter = 'all';
    state.sortBy = 'newest';

    const searchInput = document.getElementById('search-input');
    if (searchInput) searchInput.value = '';

    const deptSelect = document.getElementById('filter-department');
    if (deptSelect) deptSelect.value = '';

    const areaSelect = document.getElementById('filter-area');
    if (areaSelect) areaSelect.value = '';

    const sortSelect = document.getElementById('sort-by');
    if (sortSelect) sortSelect.value = 'newest';

    const statusBtns = document.querySelectorAll('.status-pill-btn');
    statusBtns.forEach(b => {
        b.classList.toggle('active', b.getAttribute('data-status') === 'all');
    });

    applyFilters();
}

function updateFeedbackBar() {
    const bar = document.getElementById('filter-feedback-bar');
    const text = document.getElementById('filter-count-text');
    const isFiltered = state.searchQuery || state.departmentFilter || state.areaFilter || state.statusFilter !== 'all';

    if (bar && text) {
        if (isFiltered) {
            bar.classList.remove('d-none');
            bar.classList.add('d-flex');
            text.textContent = `Showing ${state.filteredOpportunities.length} of ${state.opportunities.length} opportunities`;
        } else {
            bar.classList.add('d-none');
            bar.classList.remove('d-flex');
        }
    }
}

// ==============================================================================
// Rendering Grid Cards
// ==============================================================================
function renderOpportunityCards() {
    const grid = document.getElementById('opportunities-grid');
    const emptyState = document.getElementById('empty-state');
    if (!grid) return;

    if (state.filteredOpportunities.length === 0) {
        grid.innerHTML = '';
        renderEmptyState(false);
        return;
    }

    if (emptyState) emptyState.classList.add('d-none');

    // Dynamically balance grid layout when 2 or 1 items are displayed
    grid.classList.toggle('has-2-items', state.filteredOpportunities.length === 2);
    grid.classList.toggle('has-1-item', state.filteredOpportunities.length === 1);

    grid.innerHTML = state.filteredOpportunities.map(opp => createCardHTML(opp)).join('');

    // Attach card event listeners
    grid.querySelectorAll('.btn-view-card').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const id = parseInt(btn.getAttribute('data-id'), 10);
            viewOpportunityDetails(id);
        });
    });

    grid.querySelectorAll('.btn-edit-card').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const id = parseInt(btn.getAttribute('data-id'), 10);
            openEditModal(id);
        });
    });

    grid.querySelectorAll('.btn-toggle-status-card').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const id = parseInt(btn.getAttribute('data-id'), 10);
            const status = btn.getAttribute('data-status');
            toggleOpportunityStatus(id, status);
        });
    });

    grid.querySelectorAll('.btn-delete-card').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const id = parseInt(btn.getAttribute('data-id'), 10);
            openDeleteModal(id);
        });
    });
}

function createCardHTML(opp) {
    const isOpen = opp.status === 'Open';
    const statusBadge = isOpen
        ? `<span class="status-badge status-badge-open"><span class="status-dot"></span>Open</span>`
        : `<span class="status-badge status-badge-closed"><span class="status-dot"></span>Closed</span>`;

    const skills = (opp.required_skills || '')
        .split(',')
        .map(s => s.trim())
        .filter(Boolean)
        .slice(0, 4); // Display up to 4 on card face

    const skillsHTML = skills.map(s => `<span class="skill-chip">${escapeHtml(s)}</span>`).join('');

    // Faculty initials for avatar
    const initials = (opp.faculty_name || 'Dr')
        .replace(/^(dr|prof|engr)\.?\s*/i, '')
        .split(' ')
        .map(n => n[0])
        .slice(0, 2)
        .join('')
        .toUpperCase() || 'FA';

    // Format deadline
    const deadlineFormatted = opp.application_deadline || 'Open';

    return `
    <article class="opportunity-card" id="opportunity-card-${opp.id}">
        <div>
            <!-- Top Bar: Department & Status -->
            <div class="card-top-bar">
                <span class="department-badge">
                    <i class="bi bi-mortarboard"></i> ${escapeHtml(opp.department)}
                </span>
                ${statusBadge}
            </div>

            <!-- Title & Research Area -->
            <h3 class="card-title btn-view-card" data-id="${opp.id}" title="${escapeHtml(opp.title)}">
                ${escapeHtml(opp.title)}
            </h3>
            <div class="card-area">
                <i class="bi bi-diagram-3"></i> ${escapeHtml(opp.research_area)}
            </div>

            <!-- Description -->
            <p class="card-description">
                ${escapeHtml(opp.description)}
            </p>

            <!-- Faculty Info -->
            <div class="faculty-info-row">
                <div class="faculty-avatar">${initials}</div>
                <div>
                    <div class="faculty-name">${escapeHtml(opp.faculty_name)}</div>
                    <div class="faculty-sub">${escapeHtml(opp.department)}</div>
                </div>
            </div>

            <!-- Skills -->
            <div class="skills-container">
                ${skillsHTML}
            </div>
        </div>

        <div>
            <!-- Metadata: Positions & Deadline -->
            <div class="card-footer-meta">
                <span class="meta-pill text-dark" title="Positions available">
                    <i class="bi bi-person-fill-check text-primary"></i> ${opp.available_positions} Position${opp.available_positions > 1 ? 's' : ''}
                </span>
                <span class="meta-pill text-muted" title="Application deadline">
                    <i class="bi bi-calendar3"></i> ${deadlineFormatted}
                </span>
            </div>

            <!-- Card Action Buttons -->
            <div class="card-actions-row">
                <button type="button" class="btn btn-outline-primary flex-fill btn-view-card" data-id="${opp.id}">
                    <i class="bi bi-eye"></i> Details
                </button>
                <button type="button" class="btn btn-outline-secondary btn-edit-card" data-id="${opp.id}" title="Edit opportunity">
                    <i class="bi bi-pencil"></i>
                </button>
                <button type="button" class="btn ${isOpen ? 'btn-outline-warning' : 'btn-outline-success'} btn-toggle-status-card" data-id="${opp.id}" data-status="${opp.status}" title="${isOpen ? 'Close applications' : 'Reopen opportunity'}">
                    <i class="bi ${isOpen ? 'bi-lock' : 'bi-unlock'}"></i>
                </button>
                <button type="button" class="btn btn-outline-danger btn-delete-card" data-id="${opp.id}" title="Delete opportunity">
                    <i class="bi bi-trash3"></i>
                </button>
            </div>
        </div>
    </article>
    `;
}

function renderEmptyState(isError = false, customTitle = null, customDesc = null) {
    const emptyState = document.getElementById('empty-state');
    const titleEl = document.getElementById('empty-state-title');
    const descEl = document.getElementById('empty-state-desc');

    if (!emptyState) return;

    emptyState.classList.remove('d-none');
    if (customTitle && titleEl) titleEl.textContent = customTitle;
    if (customDesc && descEl) descEl.textContent = customDesc;

    if (!customTitle && titleEl) {
        titleEl.textContent = state.searchQuery || state.departmentFilter || state.areaFilter || state.statusFilter !== 'all'
            ? 'No Matching Opportunities'
            : 'No Research Opportunities Found';
    }

    if (!customDesc && descEl) {
        descEl.textContent = state.searchQuery || state.departmentFilter || state.areaFilter || state.statusFilter !== 'all'
            ? 'Try adjusting your search criteria or resetting filters to find available positions.'
            : 'There are currently no research opportunities recorded in the database. Be the first faculty member to post one!';
    }
}

function setLoading(isLoading) {
    state.isLoading = isLoading;
    const loader = document.getElementById('loading-state');
    const grid = document.getElementById('opportunities-grid');
    if (loader) loader.classList.toggle('d-none', !isLoading);
    if (grid && isLoading) grid.innerHTML = '';
}

// ==============================================================================
// CRUD Operation Handlers
// ==============================================================================

// 1. CREATE OPPORTUNITY (POST)
async function handleCreateSubmit(e) {
    e.preventDefault();
    const form = e.target;
    const errorBox = document.getElementById('create-form-error');
    if (errorBox) errorBox.classList.add('d-none');

    const formData = new FormData(form);
    const payload = {
        title: formData.get('title')?.trim(),
        description: formData.get('description')?.trim(),
        research_area: formData.get('research_area')?.trim(),
        faculty_name: formData.get('faculty_name')?.trim(),
        department: formData.get('department')?.trim(),
        required_skills: formData.get('required_skills')?.trim(),
        available_positions: parseInt(formData.get('available_positions'), 10),
        application_deadline: formData.get('application_deadline'),
        status: formData.get('status') || 'Open'
    };

    // Client-side pre-validation
    const clientErrors = validateOpportunityForm(payload);
    if (clientErrors.length > 0) {
        form.classList.add('was-validated');
        displayFormError(errorBox, clientErrors.join('<br>'));
        return;
    }

    const submitBtn = document.getElementById('btn-submit-create');
    if (submitBtn) submitBtn.disabled = true;

    try {
        const response = await fetch(`${API_BASE_URL}/opportunities`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const resData = await response.json();

        if (response.status === 201) {
            showToast('Research opportunity created successfully!', 'success');
            form.reset();
            if (createModalInstance) createModalInstance.hide();
            await fetchOpportunities();
        } else {
            const msg = resData.messages
                ? Object.values(resData.messages).join('<br>')
                : (resData.error || 'Failed to create opportunity.');
            displayFormError(errorBox, msg);
        }
    } catch (err) {
        displayFormError(errorBox, `Network Error: ${err.message}`);
    } finally {
        if (submitBtn) submitBtn.disabled = false;
    }
}

// 2. VIEW DETAILS (GET by ID)
async function viewOpportunityDetails(id) {
    state.activeViewId = id;
    try {
        const response = await fetch(`${API_BASE_URL}/opportunities/${id}`);
        if (!response.ok) {
            throw new Error(`Failed to load opportunity (HTTP ${response.status})`);
        }
        const opp = await response.json();

        document.getElementById('view-title').textContent = opp.title;
        document.getElementById('view-department').innerHTML = `<i class="bi bi-mortarboard"></i> ${escapeHtml(opp.department)}`;
        document.getElementById('view-area').textContent = opp.research_area;
        document.getElementById('view-faculty').textContent = opp.faculty_name;
        document.getElementById('view-positions').textContent = `${opp.available_positions} Position${opp.available_positions > 1 ? 's' : ''}`;
        document.getElementById('view-deadline').textContent = opp.application_deadline;
        document.getElementById('view-description').textContent = opp.description;

        const statusBadgeContainer = document.getElementById('view-status-badge');
        if (statusBadgeContainer) {
            statusBadgeContainer.innerHTML = opp.status === 'Open'
                ? `<span class="status-badge status-badge-open"><span class="status-dot"></span>Open</span>`
                : `<span class="status-badge status-badge-closed"><span class="status-dot"></span>Closed</span>`;
        }

        const skillsContainer = document.getElementById('view-skills');
        if (skillsContainer) {
            const skills = (opp.required_skills || '').split(',').map(s => s.trim()).filter(Boolean);
            skillsContainer.innerHTML = skills.map(s => `<span class="skill-chip">${escapeHtml(s)}</span>`).join('');
        }

        const toggleBtn = document.getElementById('btn-view-toggle-status');
        if (toggleBtn) {
            toggleBtn.innerHTML = opp.status === 'Open'
                ? '<i class="bi bi-lock"></i> Close Applications'
                : '<i class="bi bi-unlock"></i> Reopen Opportunity';
        }

        if (viewModalInstance) viewModalInstance.show();
    } catch (err) {
        showToast(`Could not fetch details: ${err.message}`, 'danger');
    }
}

// 3. EDIT OPPORTUNITY (PUT)
async function openEditModal(id) {
    state.activeEditId = id;
    const errorBox = document.getElementById('edit-form-error');
    if (errorBox) errorBox.classList.add('d-none');

    try {
        const response = await fetch(`${API_BASE_URL}/opportunities/${id}`);
        if (!response.ok) throw new Error('Could not fetch opportunity for editing.');
        const opp = await response.json();

        document.getElementById('edit-id').value = opp.id;
        document.getElementById('edit-title').value = opp.title;
        document.getElementById('edit-faculty').value = opp.faculty_name;
        document.getElementById('edit-department').value = opp.department;
        document.getElementById('edit-area').value = opp.research_area;
        document.getElementById('edit-positions').value = opp.available_positions;
        document.getElementById('edit-deadline').value = opp.application_deadline;
        document.getElementById('edit-status').value = opp.status;
        document.getElementById('edit-skills').value = opp.required_skills;
        document.getElementById('edit-description').value = opp.description;

        if (editModalInstance) editModalInstance.show();
    } catch (err) {
        showToast(err.message, 'danger');
    }
}

async function handleEditSubmit(e) {
    e.preventDefault();
    const form = e.target;
    const errorBox = document.getElementById('edit-form-error');
    if (errorBox) errorBox.classList.add('d-none');

    const id = document.getElementById('edit-id').value;
    const formData = new FormData(form);

    const payload = {
        title: formData.get('title')?.trim(),
        description: formData.get('description')?.trim(),
        research_area: formData.get('research_area')?.trim(),
        faculty_name: formData.get('faculty_name')?.trim(),
        department: formData.get('department')?.trim(),
        required_skills: formData.get('required_skills')?.trim(),
        available_positions: parseInt(formData.get('available_positions'), 10),
        application_deadline: formData.get('application_deadline'),
        status: formData.get('status')
    };

    const clientErrors = validateOpportunityForm(payload);
    if (clientErrors.length > 0) {
        form.classList.add('was-validated');
        displayFormError(errorBox, clientErrors.join('<br>'));
        return;
    }

    const submitBtn = document.getElementById('btn-submit-edit');
    if (submitBtn) submitBtn.disabled = true;

    try {
        const response = await fetch(`${API_BASE_URL}/opportunities/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const resData = await response.json();

        if (response.ok) {
            showToast('Opportunity updated successfully!', 'success');
            if (editModalInstance) editModalInstance.hide();
            await fetchOpportunities();
        } else {
            const msg = resData.messages
                ? Object.values(resData.messages).join('<br>')
                : (resData.error || 'Failed to update opportunity.');
            displayFormError(errorBox, msg);
        }
    } catch (err) {
        displayFormError(errorBox, `Network Error: ${err.message}`);
    } finally {
        if (submitBtn) submitBtn.disabled = false;
    }
}

// 4. TOGGLE STATUS (Open <-> Closed)
async function toggleOpportunityStatus(id, currentStatus) {
    const newStatus = currentStatus === 'Open' ? 'Closed' : 'Open';
    try {
        const response = await fetch(`${API_BASE_URL}/opportunities/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: newStatus })
        });

        if (response.ok) {
            showToast(`Status changed to ${newStatus}`, 'info');
            await fetchOpportunities();
        } else {
            const data = await response.json();
            showToast(data.error || 'Failed to update status', 'danger');
        }
    } catch (err) {
        showToast(`Error updating status: ${err.message}`, 'danger');
    }
}

// 5. DELETE OPPORTUNITY
function openDeleteModal(id) {
    state.activeDeleteId = id;
    const opp = state.opportunities.find(o => o.id === id);
    const titleEl = document.getElementById('delete-opportunity-title');
    if (titleEl && opp) {
        titleEl.textContent = `"${opp.title}"`;
    }
    if (deleteModalInstance) deleteModalInstance.show();
}

async function handleConfirmDelete() {
    if (!state.activeDeleteId) return;
    const id = state.activeDeleteId;
    const confirmBtn = document.getElementById('btn-confirm-delete');
    if (confirmBtn) confirmBtn.disabled = true;

    try {
        const response = await fetch(`${API_BASE_URL}/opportunities/${id}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            showToast('Opportunity deleted successfully.', 'success');
            if (deleteModalInstance) deleteModalInstance.hide();
            await fetchOpportunities();
        } else {
            const data = await response.json();
            showToast(data.error || 'Failed to delete opportunity.', 'danger');
        }
    } catch (err) {
        showToast(`Delete Error: ${err.message}`, 'danger');
    } finally {
        if (confirmBtn) confirmBtn.disabled = false;
        state.activeDeleteId = null;
    }
}

// ==============================================================================
// Validation & Utility Helpers
// ==============================================================================
function validateOpportunityForm(data) {
    const errors = [];
    if (!data.title) errors.push('Title is required.');
    if (!data.faculty_name) errors.push('Faculty lead name is required.');
    if (!data.department) errors.push('Department is required.');
    if (!data.research_area) errors.push('Research area is required.');
    if (!data.required_skills) errors.push('At least one required skill is required.');
    if (!data.description) errors.push('Description is required.');
    
    if (isNaN(data.available_positions) || data.available_positions <= 0) {
        errors.push('Available positions must be a positive integer greater than zero.');
    }

    if (!data.application_deadline) {
        errors.push('Application deadline is required.');
    } else {
        const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
        if (!dateRegex.test(data.application_deadline)) {
            errors.push('Application deadline must be formatted as YYYY-MM-DD.');
        }
    }

    if (data.status && !['Open', 'Closed'].includes(data.status)) {
        errors.push('Status must be either Open or Closed.');
    }

    return errors;
}

function displayFormError(errorBox, htmlMessage) {
    if (errorBox) {
        errorBox.innerHTML = htmlMessage;
        errorBox.classList.remove('d-none');
    }
}

function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const iconMap = {
        success: 'bi-check-circle-fill text-success',
        danger: 'bi-exclamation-circle-fill text-danger',
        warning: 'bi-exclamation-triangle-fill text-warning',
        info: 'bi-info-circle-fill text-primary'
    };

    const toastEl = document.createElement('div');
    toastEl.className = 'custom-toast';
    toastEl.innerHTML = `
        <i class="bi ${iconMap[type] || 'bi-info-circle-fill'} fs-5"></i>
        <div class="flex-grow-1 small fw-semibold text-dark">${escapeHtml(message)}</div>
        <button type="button" class="btn-close btn-close-sm" aria-label="Close"></button>
    `;

    const closeBtn = toastEl.querySelector('.btn-close');
    closeBtn.addEventListener('click', () => toastEl.remove());

    container.appendChild(toastEl);

    // Auto dismiss after 4 seconds
    setTimeout(() => {
        if (toastEl.parentElement) {
            toastEl.style.opacity = '0';
            toastEl.style.transition = 'opacity 0.3s ease';
            setTimeout(() => toastEl.remove(), 300);
        }
    }, 4000);
}

function escapeHtml(str) {
    if (typeof str !== 'string') return str || '';
    return str
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}
