# IPRO SDK Documentation Website

This folder contains the GitHub Pages documentation site for the IPRO SDK.

> **📋 Note:** SDK source code is hosted on internal GitLab. This site provides documentation only.

## 🚀 Deployment to GitHub Pages

### Step 1: Create a new GitHub repository for documentation

```bash
# Create a new repository on GitHub (e.g., ipro-sdk-docs)
# Then push this folder as the main content

cd gh-pages
git init
git add .
git commit -m "Initial documentation site"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/ipro-sdk-docs.git
git push -u origin main
```

### Step 2: Enable GitHub Pages

1. Go to your GitHub repository Settings → Pages
2. Source: Select `main` branch, `/ (root)` folder
3. Save

Your site will be available at: `https://YOUR_USERNAME.github.io/ipro-sdk-docs/`

### Step 3: Update baseurl in _config.yml

```yaml
baseurl: "/ipro-sdk-docs"  # Change to your repository name
```

### Alternative: Use GitHub Actions

Create `.github/workflows/pages.yml` in your documentation repository:
```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Ruby
        uses: ruby/setup-ruby@v1
        with:
          ruby-version: '3.1'
          bundler-cache: true
      
      - name: Build site
        run: bundle exec jekyll build
      
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v2
        with:
          path: ./_site

  deploy:
    runs-on: ubuntu-latest
    needs: build
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v3
```

## 🔄 Syncing Documentation with Internal GitLab

When SDK documentation is updated on internal GitLab, sync to GitHub:

```bash
# In your internal GitLab SDK repository
cd /path/to/ipro_sdk/gh-pages

# Copy to your GitHub docs repository
cp -r * /path/to/github-docs-repo/

# Commit and push to GitHub
cd /path/to/github-docs-repo
git add .
git commit -m "Sync documentation from internal SDK"
git push
```

Or create a CI/CD job in GitLab to auto-sync (if network allows).

## 📁 Structure

```
gh-pages/
├── _config.yml           # Jekyll configuration
├── _layouts/
│   └── default.html      # Main layout template
├── assets/
│   ├── css/
│   │   └── style.css     # Custom styles
│   ├── js/
│   │   └── main.js       # JavaScript functionality
│   └── favicon.svg       # Site favicon
├── index.html            # Home page
├── getting-started.html  # Getting started guide
├── architecture.html     # Architecture overview
├── ble-development.html  # BLE development guide
├── zephyr-rtos.html      # Zephyr RTOS guide
├── applications.html     # Application examples
├── api-reference.html    # API reference
├── Gemfile               # Ruby dependencies
└── README.md             # This file
```

## 🛠️ Local Development

### Prerequisites
- Ruby 2.7+ and Bundler
- Jekyll 4.0+

### Setup
```bash
cd gh-pages
bundle install
```

### Run locally
```bash
bundle exec jekyll serve
```

Open http://localhost:4000 in your browser.

### Build
```bash
bundle exec jekyll build
```

The built site will be in `_site/` directory.

## 🎨 Customization

### Update site info
Edit `_config.yml`:
- `title`: Site title
- `description`: Site description
- `baseurl`: Repository name (for GitHub Pages)
- `url`: Your GitHub Pages URL

### Modify styles
Edit `assets/css/style.css` to customize:
- Colors (CSS variables at the top)
- Typography
- Layout
- Components

### Add new pages
1. Create a new `.html` file
2. Add front matter:
   ```yaml
   ---
   layout: default
   title: Page Title
   ---
   ```
3. Add your content

## 📝 Content Guidelines

- Use semantic HTML with proper heading hierarchy
- Include code examples with syntax highlighting
- Add navigation sidebar for long pages
- Keep mobile responsiveness in mind

## 🔗 Important Links

- [Jekyll Documentation](https://jekyllrb.com/docs/)
- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [Liquid Template Language](https://shopify.github.io/liquid/)

## 📋 Important Notes

- **SDK Source Code**: Hosted on internal GitLab (not publicly accessible)
- **Documentation Site**: This site, hosted on GitHub Pages (public)
- **Updates**: Documentation should be synced when SDK updates are released

## 📄 License

This documentation is part of the IPRO SDK and follows the same license terms.
