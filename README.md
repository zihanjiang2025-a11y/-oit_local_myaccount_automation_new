# Brown MyAccount Automation

Command-line automation for Brown University MyAccount administrative workflows. The tool opens Chrome, signs in to MyAccount, loads users from a CSV workspace, and lets an operator search users, extract identity/status fields, review Admin IDs, and perform supported Admin ID edits. The repository includes one-click setup and launcher scripts for both macOS and Windows.

## Before You Start

Use this only with an authorized Brown MyAccount admin account. The automation operates in a real browser session and can make real Admin ID changes after the confirmation CSV is validated.

You need:

- Python 3.12
- Google Chrome
- VPN access required for MyAccount if not on Brown's network
- A Brown account with permission to view and edit the target MyAccount pages
- Modern CSV (free) editor to read and edit CSV files (optional but strongly recommended). Available at `https://www.moderncsv.com/download/`.

## Quick Start: Click-to-Setup, Then Click-to-Run

Use the setup script once on each computer. After setup finishes, use the run script whenever you want to start the tool.

### macOS

1. Install Python 3.12.
2. Clone or download this repository.
3. Create a `.env` file from `.env.example` in the project root.
4. Fill in your Brown MyAccount credentials.
5. Double-click `Setup.command`.
6. Wait for `Setup complete. Press Enter to close this window.`
7. Add users to `data/workspace.csv`.
8. Double-click `Run.command` whenever you want to start the tool.

If macOS blocks the script the first time, right-click `Setup.command`, choose **Open**, then confirm that you want to open it.

---

### Windows

1. Install Python 3.12 (64-bit).
2. Clone or download this repository.
3. Create a `.env` file from `.env.example` in the project root.
4. Fill in your Brown MyAccount credentials.
5. Double-click `Setup.bat`.
6. Wait for `Setup complete.`
7. Add users to `data/workspace.csv`.
8. Double-click `Run.bat` whenever you want to start the tool.

Setup creates the `.venv` Python environment, installs dependencies, and creates the required `data` files and folders. Run starts the interactive `myaccount>` shell.


### Manual Setup (Advanced):
Only use manual setup if the setup guides above didn't work.
1. From the project folder, create and activate a virtual environment.

On macOS or Linux:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

On Windows, use Command Prompt:

```bat
py -3.12 -m venv .venv
.venv\Scripts\activate.bat
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root from `.env.example`.

On macOS or Linux:

```bash
cp .env.example .env
```

On Windows Command Prompt:

```bat
copy .env.example .env
```

Then open `.env` and replace the example values with your MyAccount credentials:

```env
MYACCOUNT_USERNAME=your_brown_username
MYACCOUNT_PASSWORD=your_brown_password
```

4. Before running the program for the first time, create the required `data` files and folders:

On macOS, Linux, or Windows after activating the virtual environment:

```bash
python main.py setup
```

This creates `data/workspace.csv`, `data/admin_id_workspace.csv`, `data/current_admin_id_result.csv`, `data/admin_id_archive/`, and `data/chrome_profile/` if they do not already exist.


## Prepare the Workspace CSV

Make sure `data/workspace.csv` is created before running the tool. Each row represents one user. Include whichever columns you want to use for searching or extraction.

Modern CSV is recommended for this file because it automatically refreshes when the Python program updates the CSV. That matters for this workflow: commands such as `find-users`, `extract-ids`, `extract-status`, `get-admin-ids`, and `save` can modify output files while the tool is still running, and Modern CSV lets you see those updates without closing and reopening the file. 

Common search columns:

- `brown_id`
- `brown_login`
- `brown_netid`
- `brown_email`
- `first_name`
- `last_name`
- `banner_id`
- `emp_wd_src_id`
- `adv_src_id`
- `barcode`
- `personal_email`
- `iso`
- `ssn4`

Example:

```csv
brown_id,brown_login,first_name,last_name,source
123456789,jcarberr,Josiah,Carberry,banner
987654321,jsmith,Jane,Smith,oim
```

The tool updates `data/workspace.csv` when you run commands such as `find-users`, `extract-ids`, `extract-status`, or `save`.

## Run the Tool

Recommended click-to-run launchers:

- macOS: double-click `Run.command`
- Windows: double-click `Run.bat`

Or start the shell manually from an activated virtual environment:

```bash
python main.py
```

Chrome will open and the tool will log in to MyAccount. Wait until you see:

```text
myaccount>
```

Enter one command at a time. During a running task, Selenium may switch browser tabs. Wait for the `myaccount>` prompt before entering the next command.

To quit:

```text
exit
```

## Workflow

1. Put users into `data/workspace.csv`.
2. Double-click `Run.command` on Mac or `Run.bat` on Windows.
3. Search for users with `find-users`. (Required before any other tasks)
4. Extract any missing identifiers or statuses.
5. Review and save the updated workspace.
6. For Admin ID work, generate and carefully review the confirmation CSV before allowing edits.
7. If needed, replace the current users in `data/workspace.csv` with a new list of users,
    reload the users, and repeat the steps above.

Example session:

```text
myaccount> find-users brown_id
myaccount> extract-ids brown_login source
myaccount> extract-status all_short_status
myaccount> save
myaccount> get-admin-ids APP_CODE
```

## Commands

### `find-users`

Searches MyAccount for all users in `data/workspace.csv`.

Interactive:

```text
myaccount> find-users
```

The shell will ask which fields to search by. You can enter up to 3 search rounds. Use commas to combine fields in one round.

One-line:

```text
myaccount> find-users brown_id
myaccount> find-users brown_login brown_id
myaccount> find-users first_name,last_name brown_id
```

Each argument is one search round. `first_name,last_name` means one round that searches with both fields together.

### `extract-ids`

Extracts identity fields from matched users and writes them back to the workspace.

Interactive:

```text
myaccount> extract-ids
```

One-line:

```text
myaccount> extract-ids brown_login brown_id source
```

Supported extracted fields include:

- `first_name`
- `middle_name`
- `last_name`
- `pref_first_name`
- `pref_last_name`
- `birthday`
- `brown_netid`
- `brown_login`
- `brown_email`
- `personal_email`
- `personal_cell`
- `brown_id`
- `source`

### `extract-status`

Extracts status fields for matched users.

```text
myaccount> extract-status
myaccount> extract-status all_short_status
myaccount> extract-status all_status
```

Supported options:

- `all_short_status`
- `all_status`

### `get-admin-ids`

Gets current Admin IDs for a specific application code and writes the results to `data/current_admin_id_result.csv`.

```text
myaccount> get-admin-ids APP_CODE
```

Review the generated CSV to see each user's current Admin ID state for that application.

### `edit-admin-ids`

Generates a confirmation CSV, validates operator-entered fields, then performs supported Admin ID edits.

Supported operations:

- `add`
- `revoke`

`purge` appears in the shell menu, but purge is not currently supported by the implementation.

Run:

```text
myaccount> edit-admin-ids APP_CODE add
myaccount> edit-admin-ids APP_CODE revoke
```

The tool will:

1. Confirm the application code exists in MyAccount.
2. Write current Admin ID results to `data/current_admin_id_result.csv`.
3. Ask whether to generate confirmation rows.
4. Write confirmation rows to `data/admin_id_workspace.csv`.
5. Wait while you review and complete the CSV, and ask you to type `verify`.
6. Validate the CSV.
7. Ask you to type `ready`.
8. Perform the edit tasks in MyAccount.
9. Write a history CSV to `data/admin_id_archive/admin_id_run_YYYYMMDD_HHMMSS.csv`.

In `data/admin_id_workspace.csv`, fill all `FILL_THIS` cells, review and replace `WARNING` and `ACTION REQUIRED` with `override`,
change `confirmed` to `yes`, and do a final manual review before typing `ready` in the shell.

Dates must use `MM/DD/YYYY`.

For revoke operations, use one of these expiry reasons:

- `Revoked`
- `Terminated`
- `Transfered`

For add operations, Banner and OIM users may require attention fields. The tool validates those fields before creating tasks.

### `open-page`

Opens a MyAccount page for each active matched user.

```text
myaccount> open-page overview
myaccount> open-page student
myaccount> open-page employee
myaccount> open-page privileges
```

Common page values:

- `overview`
- `student`
- `employee`
- `affiliate`
- `privileges`
- `privilegehistory`
- `roles`
- `groups`
- `history`

### `save`

Writes current in-memory user records back to `data/workspace.csv`.

```text
myaccount> save
```

### `reload`

Reloads users from `data/workspace.csv`.

```text
myaccount> reload
```

Aliases:

```text
myaccount> reload-user
myaccount> reload-users
myaccount> reload user
```

### `stop`

Shows stop instructions when no task is running.

```text
myaccount> stop
```

During a running task, press `Ctrl+C` to stop the current task and return to the shell. The browser session stays open.

### `help`

Prints available commands.

```text
myaccount> help
```

## Output Files

- `data/workspace.csv`: Main user workspace. Updated by search, extraction, and save commands.
- `data/current_admin_id_result.csv`: Current Admin ID results for the last `get-admin-ids` or `edit-admin-ids` application check.
- `data/admin_id_workspace.csv`: Confirmation file generated by `edit-admin-ids`.
- `data/admin_id_archive/admin_id_run_YYYYMMDD_HHMMSS.csv`: History log for each Admin ID edit run.
- `data/chrome_profile/`: Persistent Chrome profile used by Selenium.

## Safety Checklist for Admin ID Edits

Before typing `ready`:

- Confirm the application code and application name are correct.
- Confirm every `brown_id` and `brown_login` matches the intended user.
- Confirm `operation` is correct for every row.
- Confirm every row has `confirmed` set to `yes`.
- Confirm required comments, performed-by fields, dates, and expiry reasons are correct.
- Review `data/current_admin_id_result.csv` for existing Admin IDs before adding or revoking.

## Troubleshooting

If the tool fails immediately with missing environment variables, check that `.env` exists and contains `MYACCOUNT_USERNAME` and `MYACCOUNT_PASSWORD`.

If Chrome or ChromeDriver fails to start, reinstall dependencies and make sure Chrome is installed and up to date. The project uses `webdriver-manager` to download a compatible ChromeDriver.

If login times out, confirm your credentials, MyAccount access, Duo/MFA status, and network/VPN connection.

If user search returns no match, check that the workspace CSV has valid values in the fields you selected for `find-users`.

If validation keeps rewriting `data/admin_id_workspace.csv`, read the warnings printed in the shell. Protected fields such as `brown_id`, `brown_login`, `application_code`, `operation`, and extracted status fields cannot be changed in the confirmation file unless the tool explicitly asks for an override.
