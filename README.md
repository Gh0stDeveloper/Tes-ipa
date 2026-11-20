# S4NTOS INJECTOR — iOS IPA packaging experiment

### Resource customization and signing workflow

**Test project**

This repository contains a GitHub Actions workflow for updating branding resources in an already-built iOS IPA and optionally signing the resulting archive for authorized testing.

## Scope

- Prepare custom application icons and launch resources.
- Rebuild the packaged resource catalog where supported.
- Produce an updated IPA archive.
- Optionally sign with user-supplied iOS signing credentials.
- Validate archive integrity as part of the workflow.

## Important limitations

This process does **not** compile the original Swift or Objective-C source code. Repackaging and archive checks cannot guarantee that the resulting application launches or works correctly on a device. Installation requires a valid signing method appropriate to the target device.

Only upload IPA files that you are authorized to modify or redistribute. Do not commit private certificates or credentials to a public repository.

## Use

Run the relevant GitHub Actions workflow with an authorized input archive and configure any required signing secrets in repository settings.

---

**An experimental iOS packaging and branding workflow.**
