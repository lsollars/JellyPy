How-to Guides
==============

Download an interpretation request json
----------------------------------------

Interpretation requests can be downloaded in JSON in two steps.
1. Create an authenticated CIP API session using GeL credentials
2. Download interpretation request by id and version

```python
import jellypy.pyCIPAPI.auth as auth
import jellypy.pyCIPAPI.interpretation_requests as irs

session = auth.AuthenticatedCIPAPISession(
        auth_credentials={
        'username': 'your_username',
        'password': 'your_password'
    }
)

# Downloads interpretation request json 12345-1. Returns reports as v6 by default.
irjson = irs.get_interpretation_request_json(12345, 1, session=session)
```