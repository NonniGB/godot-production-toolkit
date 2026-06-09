# Contributing

Bug reports and small fixtures are the most useful contributions. Please include:

- the content graph config;
- the smallest data files that reproduce the issue;
- the command you ran;
- the expected and actual finding.

Run the package tests before opening a pull request:

```powershell
python -m unittest discover -s tests -v
```

