To set up and install WWRF_workflow with cylc:

From and interactive compute node, activate conda environment with cylc:

```bash
conda activate wx-env
```

Move to the directory with the cylc workflow:

```bash
cd <path_to_repo>/cylc-src/WWRF_workflow
```

Validate the workflow

```bash
cylc validate .
```

If that passes:

```bash
cylc install
```

It should print something identifying the installed workflow. For example:

```bash
INSTALLED WWRF_workflow/run1 from <path_to_repo>/cylc-src/WWRF_workflow
```

So your workflow ID is `WWRF_workflow/run1`

So then:

```bash
cylc scan
cylc play WWRF_workflow/run1
```