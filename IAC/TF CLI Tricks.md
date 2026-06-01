---

### Setup and Autocompletion

- **Install Autocomplete:**
  ```sh
  terraform -install-autocomplete
  ```
  - Sets up tab auto-completion. Requires logging back in.

## Format and Validate Terraform Code

- **Format Code:**
  ```sh
  terraform fmt
  ```
  - Formats code per HCL canonical standard.

- **Validate Code:**
  ```sh
  terraform validate
  ```
  - Validates code for syntax.

- **Validate Code (Skip Backend):**
  ```sh
  terraform validate -backend=false
  ```
  - Validates code while skipping backend validation.

## Initialize Terraform Working Directory

- **Initialize Directory:**
  ```sh
  terraform init
  ```
  - Initializes directory and pulls down providers.

- **Initialize Without Plugins:**
  ```sh
  terraform init -get-plugins=false
  ```
  - Initializes directory without downloading plugins.

- **Initialize Without Verifying Plugins:**
  ```sh
  terraform init -verify-plugins=false
  ```
  - Initializes directory without verifying plugins for HashiCorp signature.

## Plan, Deploy, and Cleanup Infrastructure

- **Apply Changes Automatically:**
  ```sh
  terraform apply --auto-approve
  ```
  - Applies changes without prompting for "yes".

- **Destroy Deployment Automatically:**
  ```sh
  terraform destroy --auto-approve
  ```
  - Destroys/cleans up deployment without prompting for "yes".

- **Output Deployment Plan:**
  ```sh
  terraform plan -out plan.out
  ```
  - Outputs the deployment plan to `plan.out`.

- **Apply Plan File:**
  ```sh
  terraform apply plan.out
  ```
  - Uses the `plan.out` plan file to deploy infrastructure.

- **Output Destroy Plan:**
  ```sh
  terraform plan -destroy
  ```
  - Outputs a destroy plan.

- **Target Specific Resource:**
  ```sh
  terraform apply -target=aws_instance.my_ec2
  ```
  - Applies/deploys changes to the targeted resource only.

- **Destroy Targeted Resource:**
  ```sh
  terraform destroy -target
  ```
  - Destroys the targeted resource and its dependencies only.

- **Pass Variable via Command Line:**
  ```sh
  terraform apply -var my_region_variable=us-east-1
  ```
  - Passes a variable via command line while applying a configuration.

- **Lock State File:**
  ```sh
  terraform apply -lock=true
  ```
  - Locks the state file so it can't be modified by any other Terraform apply or modification action (possible only where backend allows locking).

- **Skip Refresh:**
  ```sh
  terraform apply refresh=false
  ```
  - Helpful with large complex deployments for saving deployment time.

- **Set Parallelism:**
  ```sh
  terraform apply --parallelism=5
  ```
  - Sets the number of simultaneous resource operations.

- **Reconcile State:**
  ```sh
  terraform refresh
  ```
  - Reconciles the state in the Terraform state file with real-world resources.

- **Get Provider Information:**
  ```sh
  terraform providers
  ```
  - Gets information about providers used in the current configuration.

## Terraform Workspaces

- **Create New Workspace:**
  ```sh
  terraform workspace new mynewworkspace
  ```
  - Creates a new workspace.

- **Select Workspace:**
  ```sh
  terraform workspace select default
  ```
  - Changes to the selected workspace.

- **List Workspaces:**
  ```sh
  terraform workspace list
  ```
  - Lists all workspaces.

## Terraform State Manipulation

- **Show Resource Details:**
  ```sh
  terraform state show aws_instance.my_ec2
  ```
  - Shows details stored in Terraform state for the resource.

- **Download State File:**
  ```sh
  terraform state pull > terraform.tfstate
  ```
  - Downloads and outputs Terraform state to a file.

- **Move Resource to Different Module:**
  ```sh
  terraform state mv aws_iam_role.my_ssm_role module.custom_module
  ```
  - Moves a resource tracked via state to a different module.

- **Replace Provider:**
  ```sh
  terraform state replace-provider hashicorp/aws registry.custom.com/aws
  ```
  - Replaces an existing provider with another.

- **List Tracked Resources:**
  ```sh
  terraform state list
  ```
  - Lists all resources tracked via the current state file.

- **Remove Resource from State:**
  ```sh
  terraform state rm aws_instance.myinstace
  ```
  - Unmanages a resource by deleting it from the Terraform state file.

## Terraform Import and Outputs

- **Import Resource:**
  ```sh
  terraform import aws_instance.new_ec2_instance i-abcd1234
  ```
  - Imports an EC2 instance with ID `i-abcd1234` into the Terraform resource named `new_ec2_instance` of type `aws_instance`.

- **Import Resource into Instance:**
  ```sh
  terraform import 'aws_instance.new_ec2_instance[0]' i-abcd1234
  ```
  - Imports a real-world resource into an instance of a Terraform resource.

- **List All Outputs:**
  ```sh
  terraform output
  ```
  - Lists all outputs as stated in the code.

- **List Specific Output:**
  ```sh
  terraform output instance_public_ip
  ```
  - Lists a specific declared output.

- **List Outputs in JSON Format:**
  ```sh
  terraform output -json
  ```
  - Lists all outputs in JSON format.

## Miscellaneous Commands

- **Display Terraform Version:**
  ```sh
  terraform -version
  ```
  - Displays the Terraform binary version and warns if the version is old.

- **Update Modules:**
  ```sh
  terraform get -update=true
  ```
  - Downloads and updates modules in the "root" module.

## Terraform Console

- **Test Interpolations:**
  ```sh
  echo 'join(",",["foo","bar"])' | terraform console
  ```
  - Echoes an expression into the Terraform console and sees its expected result as output.

- **Interactive CLI:**
  ```sh
  terraform console
  ```
  - Opens an interactive CLI for testing Terraform interpolations.

- **Display Resource Attribute:**
  ```sh
  echo "aws_instance.my_ec2.public_ip" | terraform console
  ```
  - Displays the Public IP against the `my_ec2` Terraform resource as seen in the Terraform state file.

## Terraform Graph

- **Generate Dependency Graph:**
  ```sh
  terraform graph | dot -Tpng > graph.png
  ```
  - Produces a PNG diagram showing relationships and dependencies between Terraform resources in your configuration.

## Terraform Taint/Untaint

- **Taint Resource:**
  ```sh
  terraform taint aws_instance.my_ec2
  ```
  - Taints a resource to be recreated on the next apply.

- **Untaint Resource:**
  ```sh
  terraform untaint aws_instance.my_ec2
  ```
  - Removes taint from a resource.

- **Force Unlock State File:**
  ```sh
  terraform force-unlock LOCK_ID
  ```
  - Forcefully unlocks a locked state file. `LOCK_ID` is provided when locking the state file beforehand.

## Terraform Cloud

- **Login to Terraform Cloud:**
  ```sh
  terraform login
  ```
  - Obtains and saves an API token for Terraform Cloud.

- **Logout from Terraform Cloud:**
  ```sh
  terraform logout
  ```
  - Logs out of Terraform Cloud. Defaults to hostname `app.terraform.io`.

---

### Additional Points

- **Terraform Plan with Variable File:**

  ```sh
  terraform plan -var-file="variables.tfvars"
  ```

  - Uses a variable file for planning.

- **Terraform Apply with Variable File:**

  ```sh
  terraform apply -var-file="variables.tfvars"
  ```

  - Uses a variable file for applying changes.

- **Terraform State Push:**

  ```sh
  terraform state push terraform.tfstate
  ```

  - Uploads a local state file to remote storage.

- **Terraform Show:**

  ```sh
  terraform show
  ```

  - Shows the current state or plan in a human-readable form.

- **Terraform Output with Sensitive Data:**

  ```sh
  terraform output -json | jq .
  ```

  - Lists all outputs in JSON format and pretty-prints them using `jq`.

- **Terraform Validate with Variables:**

  ```sh
  terraform validate -var-file="variables.tfvars"
  ```

  - Validates the configuration with variables from a file.
