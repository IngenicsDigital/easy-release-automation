# 1. Integrating ERA into Your Project

As previously mentioned in [README](./../README.md), a beneficial use case for ERA is its integration within
a CI pipeline.

Therefore, the following sections will guide you through the process of incorporating ERA into your CI pipeline.

**However**, these instructions can also be used for setting up ERA locally on your developer machine.

## 1.1. Table of Contents

- [1. Integrating ERA into Your Project](#1-integrating-era-into-your-project)
  - [1.1. Table of Contents](#11-table-of-contents)
  - [1.2. Overview](#12-overview)
  - [1.3. Configuration of release-config.yml file](#13-configuration-of-release-configyml-file)
    - [1.3.1. Global Parameters](#131-global-parameters)
    - [1.3.2. Repository Parameters](#132-repository-parameters)
    - [1.3.3. Plugins](#133-plugins)
    - [1.3.4. Example](#134-example)
  - [1.4. Determine Type of Access to Repositories](#14-determine-type-of-access-to-repositories)
    - [1.4.1. Checkout Repositories with Project Access Tokens](#141-checkout-repositories-with-project-access-tokens)
    - [1.4.2. Checkout Repositories with Deploy Keys](#142-checkout-repositories-with-deploy-keys)

## 1.2. Overview

![Pipeline Integration](media/era-pipeline-integration.drawio.png)

The following steps are necessary (represented in diagram above):

1. Setup the credentials to checkout provided repositories defined in `release-config.yml`:

     - 1.1: For more details, see [Checkout Repositories with Project Access Tokens](#121-checkout-repositories-with-project-access-tokens)
     - 1.2: For more details, see [Checkout Repositories with Deploy Keys](#122-checkout-repositories-with-deploy-keys)

2. Install ERA into a local Python environment:

    ```bash
    python3 -m venv .venv
    . .venv/bin/activate
    pip install git+https://github.com/IngenicsDigital/easy-release-automation.git
    ```

3. Run ERA via the cli and provide a `release-config.yml`:

    ```bash
    usage: easy-release-automation [-h] [--conf CONF] [--test TEST] [--author AUTHOR] [--email EMAIL] [--global-tag-policy GLOBAL_TAG_POLICY]

    Release Automation CLI.

    optional arguments:
      -h, --help            show this help message and exit
      --conf CONF           Path to the release configuration file.
      --test TEST           determines if Test-Run is active. true/false. Overrides test_run of the global configuration.
      --author AUTHOR       author of the release. Overrides git_user_name of the global configuration.
      --email EMAIL         the author's email. Overrides git_user_email of the global configuration.
      --global-tag-policy GLOBAL_TAG_POLICY
                            'skip': skip repository if tag exists, 'ovr': override existing tag. Overrides tag_policy of the global configuration.
    ```

4. Cleanup git credential file `~/.git-credentials` if used.

The native implementation directly installs ERA into an virtual environment.
*Assumption*: The pipeline already is an isolated reproducible environment.
*Advantage*: Each plugin can be executed in a Docker (if necessary) with out conflicts by cascading Docker files.

## 1.3. Configuration of release-config.yml file

The subsequent sections provide detailed explanations of the configurations specified in
your `release-config.yml` file:

1. Global Parameters - Overview of parameters that apply across all defined repositories.
2. Repository Parameters - Specific parameters that influence how single repositories are handled.
3. Plugins - Overview for plugins defined for each repository for modifying and verification during
the release process

In addition a short `release-config.yml` example is provided.

### 1.3.1. Global Parameters

Global Parameters are accessible for all repositories.

| **Parameter**    | **Type** | **Default** | **Description**                                                                                                                      |
| ---------------- | -------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| `git_user_email` | string   | ""          | User-Email under which the release should be executed.                                                                               |
| `git_user_name`  | string   | ""          | User-Name under which the release should be executed.                                                                                |
| `tag_policy`     | string   | "skip"      | "skip": skip repository if tag exists, "ovr": override existing tag <br/>*Note*: can be individually overwritten by each repository. |
| `test_run`       | bool     | false       | true: no pushes to remote, false: changes are pushed to the remote                                                                   |

Additionally it is possible to override the global-configuration via cli-parameters:

```bash
  --test TEST           determines if Test-Run is active. true/false. Overrides test_run of the global configuration.
  --author AUTHOR       author of the release. Overrides git_user_name of the global configuration.
  --email EMAIL         the author's email. Overrides git_user_email of the global configuration.
  --global-tag-policy GLOBAL_TAG_POLICY
                        'skip': skip repository if tag exists, 'ovr': override existing tag. Overrides tag_policy of the global configuration.
```

### 1.3.2. Repository Parameters

The following table shows the parameters that can be defined for each repository.

| **Parameter**   | **Type** | **Default** | **Public** | **Description**                                                                                                                  |
| --------------- | -------- | ----------- | ---------- | -------------------------------------------------------------------------------------------------------------------------------- |
| `should_skip`   | bool     | false       | no         | "true": skips the release, "false": executes the release.                                                                        |
| `version`       | string   | ""          | yes        | version/tag                                                                                                                      |
| `url`           | string   | ""          | yes        | URL of the Repository (More details see chapter 1.4)                                                                             |
| `stable_branch` | string   | stable      | yes        | name of the stable branch (the one that is tagged)                                                                               |
| `main_branch`   | string   | main        | yes        | name of the stable branch (the one on which is actively developed)                                                               |
| `tag_message`   | string   | ""          | no         | message for the tag                                                                                                              |
| `dependencies`  | list     | []          | no         | Define dependencies (names of other repositories defined under `repositories`).                                                  |
| `meta_data`     | any      | None        | no         | Define additional data that are specific to the repository but should be available <br/>to all plugins used for this repository. |
| `tag_policy`    | str      | None        | no         | "skip": skip repository if tag exists, "ovr": override existing tag <br/>NOTE: overrides the global settings                     |
| `plugins`       | dict     | ---         | no         | Define, which plugins are executed for modification and validation. See section: *1.1.3. Plugins*                                |

**NOTE:** Specifying dependencies has an effect on the:

- release-order: if a repository_A has a dependency on repository_B, repository_B will be released first.
- information available to the Plugins: if a repository_A has a dependency on repository_B,
  plugins that are executed in repository_A have access to public-information of repository_B,
  which are:
  - `name`
  - `url`
  - `main_branch`
  - `stable_branch`

### 1.3.3. Plugins

This section of the configuration defines the plugins that are used for each repository.
For each interface one can define multiple plugins. Each plugin is initialized with the
configuration parameters described under *1.1.1. Global Parameters* and *1.1.2. Repository Parameters*.
Additionally, one can set parameters for the `run` method that can be defined as a dictionary/
key-word-arguments in the configuration file.

| **Plugin**                | **Type** | **Default**                     | **Description**                                                                                             |
| ------------------------- | -------- | ------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| `release_modification`    | list     | [{"update_requirements": None}] | Defines plugins that modify the release branch. <br/>*Default:* Updates the requirements file.              |
| `release_validation`      | list     | [{"validate_changelog": None}]  | Defines plugins that validate the release branch. <br/>*Default:* Validates if the Changelog is up-to-date. |
| `merge_back_finalization` | list     | []                              | Defines plugins that modify the merge-back branch. <br/>*Default:* No default plugin.                       |

### 1.3.4. Example

```bash
global_config:
  git_user_email: "John.Doe@example.com"
  git_user_name: "John.Doe"
  tag_policy: "skip"

repositories:
  repo-name-1:
    version: "0.0.0-rc3"
    url: "https://github.com/IngenicsDigital/easy-release-automation.git"
    stable_branch: stable
    main_branch: main
    tag_message: "your tag message"
    plugins:
      release_modification:
        - modification-plugin-name-1 {param1: val1, param2: val2, ...}
        - modification-plugin-name-2 {*kwargs*}
        - ...
      release_validation:
        - validation-plugin-name {*kwargs*}
      merge_back_finalization:
        - modification-plugin-name {*kwargs*}
  repo-name-2:
    ...
```

For a more hands-on example see [ERA Release Configuration](../era/release-config.yml).

## 1.4. Determine Type of Access to Repositories

**Note:** This description is based on GitLab, but the concept also applies to similar platforms
like GitHub and Azure DevOps.

In order to allow ERA to download repositories it requires the setup of an authentication and
authorization mechanism for the respective repositories. Two well-known options are available:

1. [**Deploy Keys**](https://docs.gitlab.com/ee/user/project/deploy_keys/>) (SSH)
2. [**Project Access Tokens**](https://docs.gitlab.com/ee/user/project/settings/project_access_tokens.html) (HTTPS)

Both have pros and cons. The following table compares the two options and the next sections
explain their individual implementation within your project after choosing one of them. For
testing ERA, Project Access Tokens might be the better option.

**However, the use of Deploy Keys
is recommended due to the fact that Project Access Token are neither encrypted nor protected when
stored on a developer machine or server-side.**

| Feature             | Deploy Keys                                                                                        | Project Access Token                                                                                        |
| ------------------- | -------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| **Purpose**         | Provides read-only or read-write access to a repository                                            | Provides read-only or read-write access to a repository.                                                    |
| **Scope**           | Repository-specific. Also shareable between multiple projects, even those are in different groups. | Project-specific and can be configured with fine-grained permissions. Always belongs to a project or group. |
| **Setup Location**  | SSH key pair generated on developer machine.                                                       | Generated on a GitLab instance.                                                                             |
| **Distribution**    | Public key must be manually added to each used repository (**requires maintainer role**.)          | Must be manually created for each used repository (**requires maintainer role**.)                           |
| **Expiration Time** | Configurable in Gitlab.                                                                            | Configurable  in Gitlab.                                                                                    |

\* *A **role** defines the permissions that a user has within a Gitlab repository.*


### 1.4.1. Checkout Repositories with Project Access Tokens

1. *For the repository provider (at least Maintainer role)* - Generate a Token for your repository:

    - In Project select **Settings > Access Tokens**
    - Select **Add new token**
    - Give the token a **Name** and optionally an expiration date (30 days as default)
    - Select **Maintainer** role
    - Select the **read- and write-repository** checkboxes
    - Click **Create Project access token** -> generates `<Your new project access token>`
    - Provide the token in the following form to whom might need access to the repository:
    `https://<token Name>:<Your new project access token>@gitlab.example.com/path/awesome_project.git`

2. *For the repository requester* - Deposit the token on your system:

      To make the token accessible it is added to the `.git-credentials`. Further information
      about this file can be found [here](https://git-scm.com/docs/git-credential). This `.
      git-credentials` file must be stored under the default path `~/.git-credentials`. In
      addition the option `credential.useHttpPath true` allows to specify credentials for
      individual repositories. e.g.:

      ```bash
        - git config --global credential.useHttpPath true
        - git config --global credential.helper "store --file ~/.git-credentials"
        - echo https://tokenName1:token1@gitlab.example.com/path/awesome_project1.git
          > ~/.git-credentials
        - echo https://tokenName2:token2@gitlab.example.com/path/awesome_project2.git
          >> ~/.git-credentials
      ```

### 1.4.2. Checkout Repositories with Deploy Keys

1. Generation of a SSH key pair (skip if an existing key pair shall be used)

    - Generating a key pair (ecdsa recommended): `ssh-keygen -t ecdsa -b 521 -C "<name>"`
    - Accept the suggested filename and directory  (For the upcoming steps: SSH key pairs are to
    be found here: `~/.ssh/`)
    - Important: Give a passphrase when using the key locally, otherwise skip this part.

2. Private key handover to the ssh-agent of the machine executing ERA. Integrate the ssh-agent on ...
    - your developer machine:
        - Start ssh agent: ```eval `ssh-agent` ```
        - Add private key to agent: `ssh-add ~/.ssh/<key>`
        - Check if key is available: `ssh-add -l`

    - or within a Gitlab CI:

        - In Project select **Settings > CI/CD**
        - Expand **Variables**
        - Select **Add variable**
        - Select **Type** = File
        - Select **Mask variable** and **Expand variable reference**
        - Give a short **description** and a arbitrary **Key** e.g. `<PROJECT>_PRIVATE_SSH_KEY_FILE`
        - Copy the private SSH key into the **Value** field
        - Click **Add variable**
        - Inside the CI pipeline file add the following lines with *Key*
        being the previously defined CI variable and *HostServer* being the host of the Repository
        to be cloned:

        ```bash
            # Install ssh-agent
            - "command -v ssh-agent >/dev/null || ( apt-get update -y && apt-get install openssh-client -y )"
            # Run ssh-agent and pass the private SSH-Key to it
            - eval "$(ssh-agent -s)"
            - chmod 400 "$ERA_PRIVATE_SSH_KEY_FILE"
            - ssh-add "$ERA_PRIVATE_SSH_KEY_FILE"
            # Create the SSH directory and ERA_PRIVATE_SSH_KEY_FILE it the right permissions
            - mkdir -p ~/.ssh && chmod 700 ~/.ssh
            # Add the SSH host keys
            - ssh-keyscan  <git@github.com> >> ~/.ssh/known_hosts
            - chmod 644 ~/.ssh/known_hosts
        ```

3. Deposit the SSH public key in a repository that shall be considered by ERA (requires Maintainer role):

    - In Project select **Settings > Repository**
    - Expand **Deploy keys**
    - Select **Add new key**
    - Paste the public key generated in step 1 and give it a name
    - Select the **Grand write permissions to this key** checkbox
    - Optional: Update the **Expiration date**

4. Enable the added deploy key from step 3 for further projects:

    - In other Project select **Settings > Repository**
    - Expand **Deploy keys**
    - Select **Privately accessible deploy keys**
    - Search for the previously added key
    - Click the **enable** button

