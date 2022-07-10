# Index of pools used in the Horizon EDA project

This repo contains a list of Pools maintained by the Horizon EDA project and other contributors. It's the source of the list of available Pools in the "Pools" dialog.

## How to add your pool

Open pull request, adding a `.yaml` file to the `pools` directory. It should look like this:
```yaml
level: community
source:
  type: github
  user: your_username
  repo: my-cool-pool
```
