import argparse
import os


def create_dir(path):
    try:
        if not os.path.isdir(path):
            os.mkdir(path)
    except OSError as e:
        print(f"failed to create '{path}' directory, error: {e}")
        raise


def generate_app_dir(app_name):
    create_dir(app_name)
    create_dir(f"./{app_name}/app")


def generate_container_file(app_name, image):
    data = f'''FROM {image}

COPY entity.container /usr/share/containers/systemd'''
    create_file(f"{app_name}/Containerfile", data)


def generate_app_container_file(app_name, image):
    data = f'''Description=
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
    create_file(f"{app_name}/{app_name}.container", data)


def create_file(path, data):
    with open(path, "w") as f:
        f.write(data)
        f.close()


def genarete_app_template(app_name, image):
    try:
        generate_app_dir(app_name)
        generate_container_file(app_name, image)
        generate_app_container_file(app_name, image)
        create_file(f"{app_name}/README.md", "")
        create_file(f"{app_name}/app/README.md", "")
    except Exception as e:
        print("failed to  create template. Err: ", e)


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
