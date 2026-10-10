# University Research Opportunity Portal — Demonstration Video Guide

## Strict Requirements
- **Maximum Duration:** Under 60 seconds (University evaluation limit).
- **Format:** MP4 (H.264 video, AAC audio if voiced).
- **Target File:** Place the recorded video in this directory as `demonstration.mp4` or provide an unlisted YouTube / Google Drive link.

---

## 60-Second Video Timeline & Script

| Time | Window | Visual Action to Perform |
|:---:|:---:|:---|
| **00:00 – 00:05** | Terminal | Show the Flask backend server running (`python backend/app.py`). Point to `http://127.0.0.1:5000`. |
| **00:05 – 00:12** | Browser | Navigate to `http://127.0.0.1:5000/portal`. Showcase the live dashboard, metric cards, and responsive card grid. |
| **00:12 – 00:22** | Create Modal | Click **"Post Opportunity"**, fill in title, department, skills, positions, and click **"Create Posting"**. Show new card appears and stats update. |
| **00:22 – 00:30** | Detail & Edit | Click **"Details"** to show project scope; open **"Edit"** modal, modify available positions (e.g. from 2 to 4), and click **"Save"**. |
| **00:30 – 00:37** | Status Toggle | Click the status lock icon to toggle status from **Open** to **Closed**. Notice the badge updates immediately. |
| **00:37 – 00:43** | Delete Modal | Click the trash icon, confirm in the delete modal. Show the opportunity card is removed. |
| **00:43 – 00:48** | Validation Error | Open the **"Post Opportunity"** modal and click submit without filling fields to display validation feedback. |
| **00:48 – 00:57** | Postman | Switch to Postman, run the **"Research Opportunity Portal"** collection runner, displaying all 10 requests passing with green checkmarks. |
| **00:57 – 01:00** | Browser | Return to the dashboard for the final closing frame. |

---

## How to Record on Ubuntu Linux

### Option 1: Built-in GNOME Screen Recorder (Easiest)
1. Press `Ctrl + Alt + Shift + R` (or press `Print Screen` and choose the video camera icon).
2. Select your application window or entire screen.
3. Click the red record button.
4. Perform the 60-second workflow above.
5. Stop recording by clicking the red circle in the top right system bar.
6. The video is automatically saved in `~/Videos/Screencasts/`.
7. Move the video here:
   ```bash
   cp ~/Videos/Screencasts/*.webm ~/24P-0610_Arslan_Tariq_CS_5C/research-opportunity-portal/demo/demonstration.webm
   ```

### Option 2: Using SimpleScreenRecorder or Kazam
Install and launch:
```bash
sudo apt install simplescreenrecorder
simplescreenrecorder &
```
Record the window and save the output directly into `demo/demonstration.mp4`.
