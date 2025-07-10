# Fraud Analytics

Runs a REST Server with `POST /predict` endpoint which predicts a given credit card statement is fraudulent or not

### Build

To get access to the below repository check with Dharaneeshwaran.Ravichandran@ibm.com or Manjunath.A.C@ibm.com

```shell
git clone git@github.ibm.com:project-pim/pim-fraud-analytics.git

cd pim-fraud-analytics/image-build
```

Download required [wheels](https://ibm.box.com/s/w0yl8bcf4ijvw6mdzpxyvsesv1f7uwu6) into current directory

```shell
podman build -t <your_registry>/fraud-analytics .

podman push <your_registry>/fraud-analytics
```
