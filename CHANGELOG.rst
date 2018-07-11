Django OIDC Authentication Plugin
=================================

Note: Currently version numbers are the version numbers tagged in the
jhuapl-boss/djangooidc repository and don't correspond to the version
used by `setup.py`.

- v1.1 : Merged in PRs and addressed an Issue
  - Merged in PR #3 and PR #9 (Replacing `render_to_response` with `render`)
  - Fixed issue #2 with `client.callback()` returning `OIDCError` instead of
    raising the exception
