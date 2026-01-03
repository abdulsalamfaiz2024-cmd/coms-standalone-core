
# HOW TO PUSH TO A DIFFERENT GITHUB ACCOUNT

Since your IDE is connected to a different account, we will use the **Terminal** to force Git to use the correct account for this specific project.

### Step 1: Get your Repository URL
Go to GitHub (logged in as the **correct** user) and copy the HTTPS URL of your new repository.
It looks like this: `https://github.com/YOUR_NEW_USERNAME/YOUR_REPO_NAME.git`

### Step 2: Run these commands
Copy and paste the following commands into your terminal, replacing the URL with your actual one.

**Important**: Notice we add the username (`YOUR_NEW_USERNAME@`) before the `github.com` part. This forces Git to ask for the password/token for *that* user.

```bash
# 1. Add the remote (Replace with your actual details)
git remote add origin https://YOUR_NEW_USERNAME@github.com/YOUR_NEW_USERNAME/YOUR_REPO_NAME.git

# 2. Push appropriately
git push -u origin main
```

### Step 3: Authenticate
When you run the push command, it will ask for a **Password**.
*   **Do NOT use your actual GitHub login password.**
*   You must use a **Personal Access Token (PAT)**.

**How to get a Token:**
1.  Go to GitHub -> Settings -> Developer Settings -> Personal access tokens -> Tokens (classic).
2.  Generate new token (classic).
3.  Select scopes: `repo` (Full control of private repositories).
4.  Copy that long string of characters.
5.  Paste it into the terminal when asked for "Password".
