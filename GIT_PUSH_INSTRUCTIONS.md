# How to Push Your Project to GitHub

Follow these steps in your terminal or command prompt inside your project directory:

1. Initialize a git repository (if not already done):
```
git init
```

2. Add all files to the repository:
```
git add .
```

3. Commit the files:
```
git commit -m "Initial commit"
```

4. Create a new repository on GitHub:
- Go to https://github.com and log in.
- Click the "+" icon and select "New repository".
- Enter a repository name and create the repo.

5. Add the remote repository URL (replace `<your-repo-url>` with your GitHub repo URL):
```
git remote add origin <your-repo-url>
```

6. Push the code to GitHub:
```
git push -u origin main
```

After this, your code will be on GitHub and you can connect it to Railway for deployment.

If you want, I can guide you through each step interactively.
