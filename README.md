To create binary, run in root of the repository directory inside the docker container:
```bash
 xvfb-run --auto-servernum --server-args='-screen 0 1024x768x16' pyinstaller --clean LDOT2.
spec
```
