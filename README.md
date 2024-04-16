# AZH Analysis


### Resources

- [columnflow](https://github.com/uhh-cms/columnflow)
- [law](https://github.com/riga/law)
- [order](https://github.com/riga/order)
- [luigi](https://github.com/spotify/luigi)

### Setting up the analysis
- Best fork a private version of repo
- git clone --recursive "URL to your repo"
- source setup.sh (may take some time when run for the first time)
- If needed create GRID proxy

### Workflow
- Create Branches for each subproject to be takled
- Push changes to private repo
- Create pull requests regularly to avoid divergencies
- Update local files regularly with git pull

### Updating Columnflow

- Go to modules/columnflow
- git pull
- git submodule update --recursive