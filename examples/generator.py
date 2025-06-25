import argparse
import os


def create_dir(path):
    try:
        if not os.path.isdir(path):
            os.mkdir(path)
    except OSError as e:
        print(f"failed to create '{path}' directory, error: {e}")
        raise


def create_file(path, data):
    with open(path, "w") as f:
        f.write(data)
        f.close()


def generate_container_file(app_name, image):
    file_content = f'''FROM {image}

COPY {app_name}.container /usr/share/containers/systemd'''
    create_file(f"{app_name}/Containerfile", file_content)


def generate_app_container_file(app_name, image):
    service = f'''Description=
Requires=
After=

[Service]
Restart=on-failure
RestartSec=60
EnvironmentFile=/etc/pim/env.conf

[Container]
Image={image}
Network=host
SecurityLabelType=unconfined_t
AutoUpdate=registry

[Install]
WantedBy=multi-user.target default.target'''
    create_file(f"{app_name}/{app_name}.container", service)


def genarete_app_template(app_name, image):
    try:
        create_dir(app_name)
        generate_container_file(app_name, image)
        generate_app_container_file(app_name, image)
        create_file(f"{app_name}/README.md", "")
        print(f"Successfully generated structure for the '{app_name}' application.\n")
    except Exception as e:
        print("failed to  create template. Err: ", e)

def log_instructions(app_name):
    print("Follow the steps below to set up your new application image:\n")

    print(f"1. Update '{app_name}/{app_name}.container' with the appropriate values.")
    print(f"2. Document the new app description and usage in the '{app_name}/README.md' file.")
    print(f"3. Create a new directory with name 'app' inside {app_name} directory.")
    print(f"4. Add a 'Containerfile' to the {app_name}/app directory.")
    print("5. Fill the 'Containerfile' with the necessary instructions to build the app image.")
    print("6. Add necessary files to the app directory as per the application's requirements.")
    print(f"7. Build the '{app_name}/app/Containerfile image and push it to your registry.")
    print(f"8. Update '{app_name}/{app_name}.container' to set 'container.Image' with the new image name generated in above step.")
    print(f"9. Build the image from '{app_name}/{app_name}/Containerfile' and push it to the registry.\n")

    print("Application image is ready for use.")


def main():
    parser = argparse.ArgumentParser(
        description="Generate template for an app.")
    parser.add_argument('--app', type=str, required=True,
                        help='Specify name of the application')
    parser.add_argument('--image', type=str, required=True,
                        help='Specify base bootc image which will be used in app')

    args = parser.parse_args()
    genarete_app_template(args.app, args.image)
    log_instructions(args.app)


if __name__ == "__main__":
    main()
