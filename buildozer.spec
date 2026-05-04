[app]
title = SR BET AI PRO
package.name = srbetapro
package.domain = org.srtech
source.dir = .
source.include_exts = py,png,jpg,kv,json
version = 2.2

# এখানে কোনো স্পেস দেবেন না, শুধু কমা দিয়ে লিখুন
requirements = python3,kivy==2.2.1

orientation = portrait
android.archs = arm64-v8a
android.api = 31
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
