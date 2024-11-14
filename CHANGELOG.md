# Changelog

## v0.11.1 - 2024-11-14

### Bug fixes

- Drop documentation_base_url and invalid Cors PostHook implementation and remove deprecation warnings. [[f75b8e0](https://github.com/NRWLDev/starlette-problem/commit/f75b8e09754db195bff76dbe85e55a097cbd2aef)]

## v0.11.0 - 2024-11-14

### Bug fixes

- **Breaking** Remove deprecated strip_debug flags. [[c6c2f5a](https://github.com/NRWLDev/starlette-problem/commit/c6c2f5a4d04cc3dae1ff21ec006c55840e359e3a)]
- Clearer deprecation warning with PostHook return type is invalid. [[d8c4160](https://github.com/NRWLDev/starlette-problem/commit/d8c4160e54c63ba38df2e40245f4f87263dcd9c2)]

## v0.10.9 - 2024-10-01

### Bug fixes

- Support include_status_codes as an inverse for exclude_status_codes. [[e09a88b](https://github.com/NRWLDev/starlette-problem/commit/e09a88b9678cf50b0acf8a7733f6a81d8f14556a)]

## v0.10.8 - 2024-10-01

### Bug fixes

- Stop deprecation warnings when flag is not explicitly set. [[6e79e5e](https://github.com/NRWLDev/starlette-problem/commit/6e79e5ebfa28e98b364cf5756d2d80c0f59b8145)]

## v0.10.7 - 2024-10-01

### Features and Improvements

- Deprecate support for strip_debug_* parameters. Introduce StripExtrasPostHook. [[d38c411](https://github.com/NRWLDev/starlette-problem/commit/d38c411f4618c265cfcde886e25a4427a6409c0b)]

## v0.10.6 - 2024-09-09

### Bug fixes

- Remove unknown classifier from metadata [[ddb0ecc](https://github.com/NRWLDev/starlette-problem/commit/ddb0eccf535acb50c65302cf40ffca37f263ade4)]

## v0.10.5 - 2024-09-09

### Miscellaneous

- Migrate from poetry to uv for dependency and build management [[3995763](https://github.com/NRWLDev/starlette-problem/commit/399576359c8be1d7d4cdf892dfd676a4d86dedfd)]
- Update changelog-gen and related configuration. [[6b31a1a](https://github.com/NRWLDev/starlette-problem/commit/6b31a1aac3cdf634dd65322815a728eca26495dc)]

## v0.10.4 - 2024-08-30

### Bug fixes

- Deprecate usage of type_base_url in rfc9457 behind the scenes [[bb2876c](https://github.com/NRWLDev/starlette-problem/commit/bb2876c364bd5958bd62ace9dd4bc98753d7122b)]

## v0.10.3 - 2024-08-29

### Miscellaneous

- Rename documentation_base_uri to documentation_uri_template [[186b3c6](https://github.com/NRWLDev/starlette-problem/commit/186b3c683a241f8e7a3ccf2f6b2bca7edf10f2b2)]

## v0.10.2 - 2024-08-29

### Bug fixes

- Pin rfc9457 correctly [[64ae57c](https://github.com/NRWLDev/starlette-problem/commit/64ae57cd818e944ecd5788fe0df572620e8ee65a)]

## v0.10.1 - 2024-08-29

### Bug fixes

- Update rfc9457 library and document strict mode and new uri support. [[1c654aa](https://github.com/NRWLDev/starlette-problem/commit/1c654aa42e51e9779aa8f3a93fdc3aa1d5913973)]

## v0.10.0 - 2024-07-23

### Miscellaneous

- **Breaking:** Update rfc9457 with fix for correct response format per spec. [[b1540d7](https://github.com/NRWLDev/starlette-problem/commit/b1540d73bb1f311cf6389b691765f79afa7b7ead)]

## v0.9.1 - 2024-07-01

### Features and Improvements

- Pass content to post hooks to support response mutation. [[#1](https://github.com/NRWLDev/starlette-problem/issues/1)] [[372dab6](https://github.com/NRWLDev/starlette-problem/commit/372dab612e2a08d92e465d536e6deadd7c4b3a50)]

## v0.9.0 - 2024-06-28

### Features and Improvements

- **Breaking:** Rework fastapi problem to support starlette. [[1ca3264](https://github.com/NRWLDev/starlette-problem/commit/1ca32642a3e119c9747925373fd940cbcd8612de)]

### Miscellaneous

## v0.8.0 - 2024-06-14

### Features and Improvements

- **Breaking:** Drop deprecated features from 0.7 release. [[79f1026](https://github.com/NRWLDev/starlette-problem/commit/79f1026e4519dd8fc7ff9091060dbf595e42f3a4)]

## v0.7.20 - 2024-05-31

### Features and Improvements

- Add support for fully qualified documentation links in type. [[0d7e353](https://github.com/NRWLDev/starlette-problem/commit/0d7e35326d1269af980d81b28545cb35a5c4cf83)]

## v0.7.19 - 2024-05-31

### Bug fixes

- Update rfc9457 and include redirect support. [[f9fe241](https://github.com/NRWLDev/starlette-problem/commit/f9fe2411aa6d1fea0397794f318503b0cc33c005)]

### Documentation

- Expand documentation to include headers and sentry information. [[555e657](https://github.com/NRWLDev/starlette-problem/commit/555e6578dc16c5895226bb36839b74cc0e34f537)]

## v0.7.18 - 2024-05-28

### Features and Improvements

- Allow handlers to return None to delegate handling of the exception to the next handler in the chain. [[dd3a252](https://github.com/NRWLDev/starlette-problem/commit/dd3a25255d5d7b4a782f30e4dbb86937778227e6)]

## v0.7.17 - 2024-05-25

### Bug fixes

- Add deprecation warnings to deprecated modules. [[#15](https://github.com/NRWLDev/starlette-problem/issues/15)] [[a23747f](https://github.com/NRWLDev/starlette-problem/commit/a23747f82fcdbcbf35a12effc977651c0c2be936)]

## v0.7.16 - 2024-05-23

### Bug fixes

- Include Problem.headers in the JSONResponse. [[95bce0c](https://github.com/NRWLDev/starlette-problem/commit/95bce0ca81b71eba6b7dd5dd18776f1ba8169f0f)]

## v0.7.15 - 2024-05-23

### Bug fixes

- rfc9457 now supports headers and status_code, no need to reimplement base classes. [[089c65f](https://github.com/NRWLDev/starlette-problem/commit/089c65fdeacd589a3db5ff4e6a095b3732054a08)]

## v0.7.14 - 2024-05-22

### Bug fixes

- Remove HTTPException subclassing, and notify starlette of Problem in exception handlers to have them properly handled in sentry integration. [[b8324fa](https://github.com/NRWLDev/starlette-problem/commit/b8324faf5c792692ad1971137a6a837b11a14010)]

## v0.7.13 - 2024-05-22

### Miscellaneous

- Multiclass inheritance from starlette.HTTPException introduces unexpected side effects in testing and middleware. [[c8b0f3d](https://github.com/NRWLDev/starlette-problem/commit/c8b0f3d291622fccf630284e57737b006ab2a7dd)]

## v0.7.12 - 2024-05-22

### Bug fixes

- Remove __str__ implementation overrides, rely on rfc9457 implementation [[fc90194](https://github.com/NRWLDev/starlette-problem/commit/fc901947bea38386240afea09731754bd1002191)]

## v0.7.11 - 2024-05-21

### Bug fixes

- Pin rfc9457 [[50bb647](https://github.com/NRWLDev/starlette-problem/commit/50bb647e6130abe8e118a9f4156d5537ae8ccdcc)]

## v0.7.10 - 2024-05-21

### Bug fixes

- Make logger optional with no base logger, allow disabling logging on exceptions. [[9da8d50](https://github.com/NRWLDev/starlette-problem/commit/9da8d50a51cc3c6d0e184ec4e374bef67936c808)]

## v0.7.9 - 2024-05-21

### Bug fixes

- Subclass rfc9457 Problems with HTTPException to support sentry_sdk starlette integrations. [[#11](https://github.com/NRWLDev/fastapi-problem/issues/11)] [[8b43192](https://github.com/NRWLDev/starlette-problem/commit/8b43192b8336b9d94164f0d1cfad9d396a6af08c)]
- Add in py.typed file so mypy/pyright acknowledge type hints. [[#12](https://github.com/NRWLDev/fastapi-problem/issues/12)] [[010f6da](https://github.com/NRWLDev/starlette-problem/commit/010f6da1b718d9397187fd8a71a225f8f155ad72)]

## v0.7.7 - 2024-05-16

### Features and Improvements

- Use rfc9457 library for base Problem implementation. [[a9cf622](https://github.com/NRWLDev/starlette-problem/commit/a9cf62209155da132a98dd8a88ac59f5a14b1028)]

## v0.7.6 - 2024-05-15

### Miscellaneous

- Deprecate code in favour of type_ on base class implementations. [[fa828a2](https://github.com/NRWLDev/starlette-problem/commit/fa828a2cf42b826018bb09769ff587bca92d146a)]

## v0.7.5 - 2024-05-13

### Bug fixes

- Fix issue where custom handlers were ignored. [[34898e7](https://github.com/NRWLDev/starlette-problem/commit/34898e79f436847145428114bd0ca7aebde83bab)]

## v0.7.4 - 2024-05-13

### Bug fixes

- Fix typo in HttpException init. [[1c7fcf9](https://github.com/NRWLDev/starlette-problem/commit/1c7fcf970cce7e208e0f74102e88a1574d2db2ad)]

## v0.7.3 - 2024-05-13

### Bug fixes

- Add missed ForbiddenProblem 403 convenience class. [[1c756ee](https://github.com/NRWLDev/starlette-problem/commit/1c756eec1c9203e219eed29a10f7359c5dbcbc35)]

## v0.7.2 - 2024-05-12

### Features and Improvements

- Add support for pre/post hooks. [[#1](https://github.com/NRWLDev/fastapi-problem/issues/1)] [[a02b7cf](https://github.com/NRWLDev/starlette-problem/commit/a02b7cf70b77feb7d300a979d27fcb9a6a0288d8)]
- Support custom exception handler functions [[#2](https://github.com/NRWLDev/fastapi-problem/issues/2)] [[95e56d1](https://github.com/NRWLDev/starlette-problem/commit/95e56d1ca78bf11aa95c29970ba155e8e418be18)]
- Implement base error class Problem [[#3](https://github.com/NRWLDev/fastapi-problem/issues/3)] [[e35bfcf](https://github.com/NRWLDev/starlette-problem/commit/e35bfcffccdf9b9564b4ec3dad6059c01e5680e5)]

## v0.7.1 - 2024-05-01

### Bug fixes

- Remove unused legacy warning [[f4f51f0](https://github.com/NRWLDev/starlette-problem/commit/f4f51f087e1ed1de30d7dfbcd2a3f80181883044)]

## v0.7.0 - 2024-05-01

### Features and Improvements

- **Breaking:** Drop support for legacy modes from web_error [[89bff61](https://github.com/NRWLDev/starlette-problem/commit/89bff61eddcb6d068c7e8a7a8cf4a231cb4bd7dc)]
