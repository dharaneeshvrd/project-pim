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
    except Exception as e:
        print("failed to  create template. Err: ", e)

def log_instructions():
    print("Please follow below steps.")
    


def main():
    parser = argparse.ArgumentParser(
        description="Generate template for an app.")
    parser.add_argument('--app', type=str, required=True,
                        help='Specify name of the application')
    parser.add_argument('--image', type=str, required=True,
                        help='Specify image which will be used in app')

    args = parser.parse_args()
    genarete_app_template(args.app, args.image)


if __name__ == "__main__":
    main()
