# 1. Getting Started For End Users

- [1. Getting Started For End Users](#1-getting-started-for-end-users)
  - [1.1. CLI Usage](#11-cli-usage)
  - [1.2. Release ERA Itself In Test Mode](#12-release-era-itself-in-test-mode)
  - [1.3. Release ERA Itself In Production Mode Via Github Fork](#13-release-era-itself-in-production-mode-via-github-fork)
  - [1.4. Release Your Project With ERA](#14-release-your-project-with-era)
  - [1.5. Further References](#15-further-references)

## 1.1. CLI Usage

```bash
    usage: easy-release-automation [-h] [--conf CONF] [--test TEST] [--author AUTHOR] [--email EMAIL] [--global-tag-policy GLOBAL_TAG_POLICY]

    Release Automation Script.

    options:
    -h, --help            show this help message and exit
    --conf CONF           Path to the release configuration file.
    --test TEST           determines if Test-Run is active. true/false. Overrides test_run of the global configuration.
    --author AUTHOR       author of the release. Overrides git_user_name of the global configuration.
    --email EMAIL         the author's email. Overrides git_user_email of the global configuration.
    --global-tag-policy GLOBAL_TAG_POLICY
                            'skip': skip repository if tag exists, 'ovr': override existing tag. Overrides tag_policy of the global configuration.
```

## 1.2. Release ERA Itself In Test Mode

1. Clone the repository

    ```bash
        git clone git@github.com:IngenicsDigital/easy-release-automation.git
    ```

2. Set up Python environment

    ```bash
        python3 -m venv .venv && . .venv/bin/activate && pip install easy-release-automation/
    ```

3. Configure release settings with release-config example `getting-started-release-config-simple.yml`

    - Copy the starter configuration file to your working directory:

    ```bash
        cp easy-release-automation/doc/media/getting-started-release-config-simple.yml .
    ```

4. Release `ERA` repository in test mode (No changes to Git remote)

    - Run ERA in test mode with the following settings:

    ```bash
        ERA_LOG_LEVEL="INFO" easy-release-automation \
            --author "John Doe" \
            --email "john.doe@example.com" \
            --test true \
            --conf  "getting-started-release-config-simple.yml"
    ```

5. Review directory layout

    - After execution, your directory should contain:

    ```bash
        ├── easy-release-automation # ERA source code
        ├── .era-repositories # Checkouts from "getting-started-release-config-simple.yml"
        │   └── easy-release-automation # Released ERA repo in test mode
        ├── getting-started-release-config-simple.yml # Your config file
        └── .venv # Python virtual environment
    ```

6. Check ERA commit results

```bash
    cd .era-repositories/easy-release-automation
    git log --oneline
```

## 1.3. Release ERA Itself In Production Mode Via Github Fork

1. Create Github fork from `https://github.com/IngenicsDigital/easy-release-automation`
2. Check out repository:

    - Create a Dedicated Branch: For testing with ERA, create a new branch named `test-era`:

    ```bash
        git checkout -b test-era
    ```

3. Customize simple ERA configuration `doc/media/getting-started-release-config-simple.yml`

    - **Global Settings**: Update the git user and email to reflect the actual user handling the release.

    - **Repository Settings**:
        - Update the repository name and URL
        - Change `main_branch: main` to `main_branch: test-era`
        - Replace line `url: git@github.com:IngenicsDigital/easy-release-automation.git`

4. Push your configuration changes to Git remote:

    ```bash
        git add . && git commit -m "chore: Update simple ERA release configuration to ERA fork"
        git push --set-upstream origin test-era
    ```

5. Release `ERA` fork repository in production mode  (**Attention:** Changes to Git remote!)

```bash
    ERA_LOG_LEVEL="INFO" easy-release-automation \
        --author "John Doe" \
        --email "john.doe@example.com" \
         --test false \
         --conf  "doc/media/getting-started-release-config-simple.yml"
```

## 1.4. Release Your Project With ERA

1. Check out your repository

    - Create a Dedicated Branch: For testing with ERA, create a new branch named `test-era`:

    ```bash
        git checkout -b test-era
    ```

2. Configure release settings

    - Copy the ERA simple configuration file to your working directory:

    ```bash
        cp getting-started-release-config-simple.yml <your-project-repo>/era/release-config.yml
    ```

3. Customize Your Configuration `<your-project-repo>/era/release-config.yml`

    - **Global Settings**: Update the git user and email to reflect the actual user handling the release.

    - **Repository Settings**:
        - Update the repository name and URL
        - Change `main_branch: main` to `main_branch: test-era`
        - Adjust paths for Changelog plugins if different from default settings.
          - Make sure that your Changelog file has a section called `## [Unreleased]`
        - Add `.era-repositories/` to `.gitignore`

4. Push your configuration changes to Git remote:

    ```bash
        git add . && git commit -m "chore: Integrate simple ERA release configuration"
        git push --set-upstream origin test-era
    ```

5. Release in Test Mode (No changes to Git remote)

    - Use correct values and replace `<TBD-REPLACE>` sections
    - Run ERA in test mode to safely simulate the release process:

    ```bash
        ERA_LOG_LEVEL="INFO" easy-release-automation \
            --author "<TBD-REPLACE>" \
            --email "<TBD-REPLACE>" \
            --test true \
            --conf  <your-project-repo>/era/release-config.yml>
    ```

6. Release in production mode (**Attention:** Changes to Git remote!)

    - Use correct values and replace `<TBD-REPLACE>` sections
    - Run ERA in test mode to safely simulate the release process:

    ```bash
        ERA_LOG_LEVEL="INFO" easy-release-automation \
            --author "<TBD-REPLACE>" \
            --email "<TBD-REPLACE>" \
            --test false \
            --conf  <your-project-repo>/era/release-config.yml>
    ```

## 1.5. Further References

- [ERA Project Integration Guide](project_integration.md)
- [How does ERA work?](overview.md)
- [Feature Matrix](features.md)
