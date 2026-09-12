Compressed Size (sample avg): 35.667712 MB
Uncompressed Size (sample avg): 194.313571 MB
Number of events per hour (sample avg): 147015.20
Compression Ratio: 5.45

One week of data: 31.88 GB

One hour of data had the following event counts

{'PullRequestReviewCommentEvent': 2179,
 'IssueCommentEvent': 4759,
 'PullRequestEvent': 15112, 
 'PushEvent': 97680, 
 'CreateEvent': 10399, 
 'IssuesEvent': 3678, 
 'PullRequestReviewEvent': 2051, 
 'WatchEvent': 4714, 
 'DeleteEvent': 4141, 
 'ForkEvent': 876, 
 'ReleaseEvent': 637, 
 'CommitCommentEvent': 103, 
 'MemberEvent': 220, 
 'GollumEvent': 64, 
 'DiscussionEvent': 35, 
 'PublicEvent': 85}

Top level key union:
{'payload', 'repo', 'type', 'actor', 'org', 'created_at', 'id', 'public'}
Top level key intersection:
{'payload', 'type', 'repo', 'actor', 'created_at', 'id', 'public'} (same, but missing 'org')

Type to payload keys mapping:
IssueCommentEvent: {'comment', 'issue', 'action'}
PullRequestEvent: {'pull_request', 'assignee', 'labels', 'number', 'assignees', 'label', 'action'}
PullRequestReviewCommentEvent: {'comment', 'pull_request', 'action'}
WatchEvent: {'action'}
ForkEvent: {'forkee', 'action'}
PushEvent: {'ref', 'push_id', 'repository_id', 'head', 'before'}
DeleteEvent: {'full_ref', 'ref', 'ref_type', 'pusher_type'}
CreateEvent: {'pusher_type', 'ref', 'master_branch', 'ref_type', 'full_ref', 'description'}
IssuesEvent: {'assignee', 'labels', 'assignees', 'issue', 'label', 'action'}
PullRequestReviewEvent: {'review', 'pull_request', 'action'}
CommitCommentEvent: {'comment', 'action'}
ReleaseEvent: {'release', 'action'}
DiscussionEvent: {'discussion', 'action'}
MemberEvent: {'member', 'action'}
GollumEvent: {'pages'}
PublicEvent: set()

Skew Analysis:
Repo ID: 1108982410, Count: 367366, Fraction: 0.0036
Repo ID: 1117703620, Count: 267134, Fraction: 0.0026
Repo ID: 1122140563, Count: 256209, Fraction: 0.0025
Repo ID: 1099385184, Count: 229220, Fraction: 0.0022
Repo ID: 1051430770, Count: 157187, Fraction: 0.0015
Repo ID: 1051442401, Count: 154825, Fraction: 0.0015
Repo ID: 970201570, Count: 140336, Fraction: 0.0014
Repo ID: 726705482, Count: 118889, Fraction: 0.0012
Repo ID: 1076470140, Count: 108941, Fraction: 0.0011
Repo ID: 996197105, Count: 103961, Fraction: 0.0010
Repo ID: 1086369682, Count: 103808, Fraction: 0.0010
Repo ID: 713192428, Count: 102633, Fraction: 0.0010
Repo ID: 1125932955, Count: 102042, Fraction: 0.0010
Repo ID: 940208378, Count: 97673, Fraction: 0.0010
Repo ID: 945142987, Count: 95654, Fraction: 0.0009
Repo ID: 1119742099, Count: 90641, Fraction: 0.0009
Repo ID: 746930940, Count: 87688, Fraction: 0.0009
Repo ID: 1081821939, Count: 73674, Fraction: 0.0007
Repo ID: 1106575222, Count: 73001, Fraction: 0.0007
Repo ID: 1037703875, Count: 72785, Fraction: 0.0007
Repo ID: 1013904109, Count: 72014, Fraction: 0.0007
Repo ID: 792877994, Count: 70462, Fraction: 0.0007
Repo ID: 1038068383, Count: 70396, Fraction: 0.0007
Repo ID: 1015761727, Count: 68950, Fraction: 0.0007
Repo ID: 529127781, Count: 68193, Fraction: 0.0007

Top 1% total count: 45944317, Fraction: 0.4494

Important JSON paths:
PR Number: event[payload][pull_request][number]
PR Creation Timestamp: event[created_at]
PR Author Login: event[actor][login]
Review submission timestamp: event[payload][review][submitted_at]
Review state: event[payload][review][state]
Repository Full Name: event[repo][name]

Example PullRequestEvent:

{
  "id": "5567787002",
  "type": "PullRequestEvent",
  "actor": {
    "id": 194618994,
    "login": "Yaduvanshy-SejalPooja",
    "display_login": "Yaduvanshy-SejalPooja",
    "gravatar_id": "",
    "url": "https://api.github.com/users/Yaduvanshy-SejalPooja",
    "avatar_url": "https://avatars.githubusercontent.com/u/194618994?"
  },
  "repo": {
    "id": 1098943721,
    "name": "srivastavAnkittt/unherited",
    "url": "https://api.github.com/repos/srivastavAnkittt/unherited"
  },
  "payload": {
    "action": "opened",
    "number": 6,
    "pull_request": {
      "url": "https://api.github.com/repos/srivastavAnkittt/unherited/pulls/6",
      "id": 3140819929,
      "number": 6,
      "head": {
        "ref": "develop",
        "sha": "ce8bcef521c0f72d76e893a0bb9449e1a20885ff",
        "repo": {
          "id": 1098943721,
          "url": "https://api.github.com/repos/srivastavAnkittt/unherited",
          "name": "unherited"
        }
      },
      "base": {
        "ref": "main",
        "sha": "32e19ff3a48a9571bbfc840a39fe2c82d8b8c804",
        "repo": {
          "id": 1098943721,
          "url": "https://api.github.com/repos/srivastavAnkittt/unherited",
          "name": "unherited"
        }
      }
    }
  },
  "public": true,
  "created_at": "2026-01-01T15:00:00Z"
}


Example PullRequestReviewEvent:

{
  "id": "5567787013",
  "type": "PullRequestReviewEvent",
  "actor": {
    "id": 41898282,
    "login": "github-actions[bot]",
    "display_login": "github-actions",
    "gravatar_id": "",
    "url": "https://api.github.com/users/github-actions[bot]",
    "avatar_url": "https://avatars.githubusercontent.com/u/41898282?"
  },
  "repo": {
    "id": 921230777,
    "name": "TuringGpt/Augment-Whisper-Slackbot",
    "url": "https://api.github.com/repos/TuringGpt/Augment-Whisper-Slackbot"
  },
  "payload": {
    "review": {
      "id": 3621903746,
      "node_id": "PRR_kwDONujduc7X4d2C",
      "user": {
        "login": "github-actions[bot]",
        "id": 41898282,
        "node_id": "MDM6Qm90NDE4OTgyODI=",
        "avatar_url": "https://avatars.githubusercontent.com/in/15368?v=4",
        "gravatar_id": "",
        "url": "https://api.github.com/users/github-actions%5Bbot%5D",
        "html_url": "https://github.com/apps/github-actions",
        "followers_url": "https://api.github.com/users/github-actions%5Bbot%5D/followers",
        "following_url": "https://api.github.com/users/github-actions%5Bbot%5D/following{/other_user}",
        "gists_url": "https://api.github.com/users/github-actions%5Bbot%5D/gists{/gist_id}",
        "starred_url": "https://api.github.com/users/github-actions%5Bbot%5D/starred{/owner}{/repo}",
        "subscriptions_url": "https://api.github.com/users/github-actions%5Bbot%5D/subscriptions",
        "organizations_url": "https://api.github.com/users/github-actions%5Bbot%5D/orgs",
        "repos_url": "https://api.github.com/users/github-actions%5Bbot%5D/repos",
        "events_url": "https://api.github.com/users/github-actions%5Bbot%5D/events{/privacy}",
        "received_events_url": "https://api.github.com/users/github-actions%5Bbot%5D/received_events",
        "type": "Bot",
        "user_view_type": "public",
        "site_admin": false
      },
      "body": "# PR Compliance Checks\nThank you for your Pull Request! We have run several checks on this pull request in order to make sure it's suitable for merging into this project.  The results are listed in the  following section.\n\n## Issue Reference In order to be consideredfor merging, the pull request description must refer to a specific issue number. This is described in our [Contributing Guide](https://github.com/Dun-sin/Whisper/blob/main/CONTRIBUTING.md). This check is looking for a phrase similar to: \"Fixes #XYZ\" or \"Resolves #XYZ\" where XYZ isthe issue number that this PR is meant to address.\n\n## Conventional Commit PR Title\nIn order to be considered for merging, the pull requesttitle must match the specification in  [conventional commits](https://www.conventionalcommits.org/en/v1.0.0/). You can edit the title in orderfor this check to pass.\nMost often, our PR titles are something like one of these:\n- docs: correct typo in README\n- feat: implement dark mode\"\n- fix: correct remove button behavior\n\nLinting Errors\n\n- Found type \"fear\", must be one of \"feat\",\"fix\",\"docs\",\"style\",\"refactor\",\"perf\",\"test\",\"build\",\"ci\",\"chore\",\"revert\"",
      "commit_id": "503751fe3d0ac5e8b5de0626bf91d6d269814c44",
      "submitted_at": "2026-01-01T15:00:00Z",
      "state": "commented",
      "html_url": "https://github.com/TuringGpt/Augment-Whisper-Slackbot/pull/315#pullrequestreview-3621903746",
      "pull_request_url": "https://api.github.com/repos/TuringGpt/Augment-Whisper-Slackbot/pulls/315",
      "_links": {
        "html": {
          "href": "https://github.com/TuringGpt/Augment-Whisper-Slackbot/pull/315#pullrequestreview-3621903746"
        },
        "pull_request": {
          "href": "https://api.github.com/repos/TuringGpt/Augment-Whisper-Slackbot/pulls/315"
        }
      },
      "updated_at": "2026-01-01T15:00:00Z"
    },
    "pull_request": {
      "url": "https://api.github.com/repos/TuringGpt/Augment-Whisper-Slackbot/pulls/315",
      "id": 3140819836,
      "number": 315,
      "head": {
        "ref": "feat/edit-product-drawer",
        "sha": "503751fe3d0ac5e8b5de0626bf91d6d269814c44",
        "repo": {
          "id": 921230777,
          "url": "https://api.github.com/repos/TuringGpt/Augment-Whisper-Slackbot",
          "name": "Augment-Whisper-Slackbot"
        }
      },
      "base": {
        "ref": "augment",
        "sha": "c468205568eb45bf245394c056b171685fd75c63",
        "repo": {
          "id": 921230777,
          "url": "https://api.github.com/repos/TuringGpt/Augment-Whisper-Slackbot",
          "name": "Augment-Whisper-Slackbot"
        }
      }
    },
    "action": "created"
  },
  "public": true,
  "created_at": "2026-01-01T15:00:01Z",
  "org": {
    "id": 140577369,
    "login": "TuringGpt",
    "gravatar_id": "",
    "url": "https://api.github.com/orgs/TuringGpt",
    "avatar_url": "https://avatars.githubusercontent.com/u/140577369?"
  }
}


Example PullRequestReviewCommentEvent:

{
  "id": "5567786996",
  "type": "PullRequestReviewCommentEvent",
  "actor": {
    "id": 175728472,
    "login": "Copilot",
    "display_login": "copilot-pull-request-reviewer",
    "gravatar_id": "",
    "url": "https://api.github.com/users/Copilot",
    "avatar_url": "https://avatars.githubusercontent.com/u/175728472?"
  },
  "repo": {
    "id": 301843635,
    "name": "thomasduchatelle/dphoto",
    "url": "https://api.github.com/repos/thomasduchatelle/dphoto"
  },
  "payload": {
    "action": "created",
    "comment": {
      "url": "https://api.github.com/repos/thomasduchatelle/dphoto/pulls/comments/2656413153",
      "pull_request_review_id": 3621903745,
      "id": 2656413153,
      "node_id": "PRRC_kwDOEf3Es86eVaXh",
      "diff_hunk": "@@ -0,0 +1,38 @@\n+// eslint-disable-next-line @typescript-eslint/triple-slash-reference\n+/// <reference path=\"./.sst/platform/config.d.ts\" />\n+\n+export default $config({\n+    app(input) {\n+        return {\n+            name: \"web-nextjs\",\n+            removal: \"remove\",\n+            protect: false,\n+            home: \"aws\",\n+        };\n+    },\n+    async run() {\n+        const distributionId = process.env.SST_DISTRIBUTION_ID;\n+\n+        console.log(`SST_DISTRIBUTION_ID=${distributionId}`)\n+        console.log(`SST_COGNITO_ISSUER=${process.env.SST_COGNITO_ISSUER}`)\n+        console.log(`SST_COGNITO_CLIENT_ID=${process.env.SST_COGNITO_CLIENT_ID}`)\n+        console.log(`SST_COGNITO_CLIENT_SECRET=${process.env.SST_COGNITO_CLIENT_SECRET}`)\n+\n+        const distribution = sst.aws.Router.get(\"CDN\", distributionId)",
      "path": "web-nextjs/sst.config.ts",
      "commit_id": "b2fc5ae0c9d6ba73ca25457b02f44562642ecfc7",
      "original_commit_id": "b2fc5ae0c9d6ba73ca25457b02f44562642ecfc7",
      "user": {
        "login": "Copilot",
        "id": 175728472,
        "node_id": "BOT_kgDOCnlnWA",
        "avatar_url": "https://avatars.githubusercontent.com/in/946600?v=4",
        "gravatar_id": "",
        "url": "https://api.github.com/users/Copilot",
        "html_url": "https://github.com/apps/copilot-pull-request-reviewer",
        "followers_url": "https://api.github.com/users/Copilot/followers",
        "following_url": "https://api.github.com/users/Copilot/following{/other_user}",
        "gists_url": "https://api.github.com/users/Copilot/gists{/gist_id}",
        "starred_url": "https://api.github.com/users/Copilot/starred{/owner}{/repo}",
        "subscriptions_url": "https://api.github.com/users/Copilot/subscriptions",
        "organizations_url": "https://api.github.com/users/Copilot/orgs",
        "repos_url": "https://api.github.com/users/Copilot/repos",
        "events_url": "https://api.github.com/users/Copilot/events{/privacy}",
        "received_events_url": "https://api.github.com/users/Copilot/received_events",
        "type": "Bot",
        "user_view_type": "public",
        "site_admin": false
      },
      "body": "The distributionId is used without validation. If SST_DISTRIBUTION_ID is undefined or empty, sst.aws.Router.get() will fail. Add a check to verify that all required environment variables are present before attempting to use them, and throw a clear error message if any are missing.",
      "created_at": "2026-01-01T15:00:00Z",
      "updated_at": "2026-01-01T15:00:03Z",
      "html_url": "https://github.com/thomasduchatelle/dphoto/pull/185#discussion_r2656413153",
      "pull_request_url": "https://api.github.com/repos/thomasduchatelle/dphoto/pulls/185",
      "_links": {
        "self": {
          "href": "https://api.github.com/repos/thomasduchatelle/dphoto/pulls/comments/2656413153"
        },
        "html": {
          "href": "https://github.com/thomasduchatelle/dphoto/pull/185#discussion_r2656413153"
        },
        "pull_request": {
          "href": "https://api.github.com/repos/thomasduchatelle/dphoto/pulls/185"
        }
      },
      "reactions": {
        "url": "https://api.github.com/repos/thomasduchatelle/dphoto/pulls/comments/2656413153/reactions",
        "total_count": 0,
        "+1": 0,
        "-1": 0,
        "laugh": 0,
        "hooray": 0,
        "confused": 0,
        "heart": 0,
        "rocket": 0,
        "eyes": 0
      },
      "original_position": 21,
      "position": 21,
      "subject_type": "line"
    },
    "pull_request": {
      "url": "https://api.github.com/repos/thomasduchatelle/dphoto/pulls/185",
      "id": 3139266627,
      "number": 185,
      "head": {
        "ref": "copilot/implement-step-3-integration-another-one",
        "sha": "b2fc5ae0c9d6ba73ca25457b02f44562642ecfc7",
        "repo": {
          "id": 301843635,
          "url": "https://api.github.com/repos/thomasduchatelle/dphoto",
          "name": "dphoto"
        }
      },
      "base": {
        "ref": "nextjs",
        "sha": "4dbf6f30120d2765f15c378f7ed899361ba85da8",
        "repo": {
          "id": 301843635,
          "url": "https://api.github.com/repos/thomasduchatelle/dphoto",
          "name": "dphoto"
        }
      }
    }
  },
  "public": true,
  "created_at": "2026-01-01T15:00:00Z"
}


Example IssueCommentEvent:

{
  "id": "5567786997",
  "type": "IssueCommentEvent",
  "actor": {
    "id": 2921215,
    "login": "cbersch",
    "display_login": "cbersch",
    "gravatar_id": "",
    "url": "https://api.github.com/users/cbersch",
    "avatar_url": "https://avatars.githubusercontent.com/u/2921215?"
  },
  "repo": {
    "id": 916632184,
    "name": "AwesomeAssertions/AwesomeAssertions",
    "url": "https://api.github.com/repos/AwesomeAssertions/AwesomeAssertions"
  },
  "payload": {
    "action": "created",
    "issue": {
      "url": "https://api.github.com/repos/AwesomeAssertions/AwesomeAssertions/issues/389",
      "repository_url": "https://api.github.com/repos/AwesomeAssertions/AwesomeAssertions",
      "labels_url": "https://api.github.com/repos/AwesomeAssertions/AwesomeAssertions/issues/389/labels{/name}",
      "comments_url": "https://api.github.com/repos/AwesomeAssertions/AwesomeAssertions/issues/389/comments",
      "events_url": "https://api.github.com/repos/AwesomeAssertions/AwesomeAssertions/issues/389/events",
      "html_url": "https://github.com/AwesomeAssertions/AwesomeAssertions/pull/389",
      "id": 3767281666,
      "node_id": "PR_kwDONqKyeM660agZ",
      "number": 389,
      "title": "Fix local build",
      "user": {
        "login": "cbersch",
        "id": 2921215,
        "node_id": "MDQ6VXNlcjI5MjEyMTU=",
        "avatar_url": "https://avatars.githubusercontent.com/u/2921215?v=4",
        "gravatar_id": "",
        "url": "https://api.github.com/users/cbersch",
        "html_url": "https://github.com/cbersch",
        "followers_url": "https://api.github.com/users/cbersch/followers",
        "following_url": "https://api.github.com/users/cbersch/following{/other_user}",
        "gists_url": "https://api.github.com/users/cbersch/gists{/gist_id}",
        "starred_url": "https://api.github.com/users/cbersch/starred{/owner}{/repo}",
        "subscriptions_url": "https://api.github.com/users/cbersch/subscriptions",
        "organizations_url": "https://api.github.com/users/cbersch/orgs",
        "repos_url": "https://api.github.com/users/cbersch/repos",
        "events_url": "https://api.github.com/users/cbersch/events{/privacy}",
        "received_events_url": "https://api.github.com/users/cbersch/received_events",
        "type": "User",
        "user_view_type": "public",
        "site_admin": false
      },
      "labels": [],
      "state": "open",
      "locked": false,
      "assignee": null,
      "assignees": [],
      "milestone": null,
      "comments": 4,
      "created_at": "2025-12-29T12:22:38Z",
      "updated_at": "2026-01-01T15:02:12Z",
      "closed_at": null,
      "type": null,
      "active_lock_reason": null,
      "draft": false,
      "pull_request": {
        "url": "https://api.github.com/repos/AwesomeAssertions/AwesomeAssertions/pulls/389",
        "html_url": "https://github.com/AwesomeAssertions/AwesomeAssertions/pull/389",
        "diff_url": "https://github.com/AwesomeAssertions/AwesomeAssertions/pull/389.diff",
        "patch_url": "https://github.com/AwesomeAssertions/AwesomeAssertions/pull/389.patch",
        "merged_at": null
      },
      "body": "<!-- Please provide a description of your changes above the IMPORTANT checklist -->\r\n\r\nFix #388 \r\n## IMPORTANT \r\n\r\n* [ ] If the PR touches the public API, the changes have been approved in a separate issue with the \"api-approved\" label.\r\n* [ ] The code complies with the [Coding Guidelines for C#](https://www.csharpcodingguidelines.com/).\r\n* [ ] The changes are covered by unit tests which follow the Arrange-Act-Assert syntax and the naming conventions such as is used [in these tests](../tree/main/Tests/AwesomeAssertions.Equivalency.Specs/MemberMatchingSpecs.cs#L51-L430).\r\n* [ ] If the PR adds a feature or fixes a bug, please update [the release notes](../tree/main/docs/_pages/releases.md) with a functional description that explains what the change means to consumers of this library, which are published on the [website](https://awesomeassertions.org/releases).\r\n* [ ] If the PR changes the public API the changes needs to be included by running [AcceptApiChanges.ps1](../tree/main/AcceptApiChanges.ps1) or [AcceptApiChanges.sh](../tree/main/AcceptApiChanges.sh).\r\n* [ ] If the PR affects [the documentation](../tree/main/docs/_pages), please include your changes in this pull request so the documentation will appear on the [website](https://awesomeassertions.org/introduction).\r\n    * [ ] Please also run `./build.sh --target spellcheck` or `.\\build.ps1 --target spellcheck` before pushing and check the good outcome\r\n\r\n## Legal checklist\r\n\r\n* [ ] This work is entirely original, it is not derived from any existing code incompatible with the Apache 2.0 License, like FluentAssertions.\r\n",
      "reactions": {
        "url": "https://api.github.com/repos/AwesomeAssertions/AwesomeAssertions/issues/389/reactions",
        "total_count": 0,
        "+1": 0,
        "-1": 0,
        "laugh": 0,
        "hooray": 0,
        "confused": 0,
        "heart": 0,
        "rocket": 0,
        "eyes": 0
      },
      "timeline_url": "https://api.github.com/repos/AwesomeAssertions/AwesomeAssertions/issues/389/timeline",
      "performed_via_github_app": null,
      "state_reason": null
    },
    "comment": {
      "url": "https://api.github.com/repos/AwesomeAssertions/AwesomeAssertions/issues/comments/3703798555",
      "html_url": "https://github.com/AwesomeAssertions/AwesomeAssertions/pull/389#issuecomment-3703798555",
      "issue_url": "https://api.github.com/repos/AwesomeAssertions/AwesomeAssertions/issues/389",
      "id": 3703798555,
      "node_id": "IC_kwDONqKyeM7cw3sb",
      "user": {
        "login": "cbersch",
        "id": 2921215,
        "node_id": "MDQ6VXNlcjI5MjEyMTU=",
        "avatar_url": "https://avatars.githubusercontent.com/u/2921215?v=4",
        "gravatar_id": "",
        "url": "https://api.github.com/users/cbersch",
        "html_url": "https://github.com/cbersch",
        "followers_url": "https://api.github.com/users/cbersch/followers",
        "following_url": "https://api.github.com/users/cbersch/following{/other_user}",
        "gists_url": "https://api.github.com/users/cbersch/gists{/gist_id}",
        "starred_url": "https://api.github.com/users/cbersch/starred{/owner}{/repo}",
        "subscriptions_url": "https://api.github.com/users/cbersch/subscriptions",
        "organizations_url": "https://api.github.com/users/cbersch/orgs",
        "repos_url": "https://api.github.com/users/cbersch/repos",
        "events_url": "https://api.github.com/users/cbersch/events{/privacy}",
        "received_events_url": "https://api.github.com/users/cbersch/received_events",
        "type": "User",
        "user_view_type": "public",
        "site_admin": false
      },
      "created_at": "2026-01-01T15:00:00Z",
      "updated_at": "2026-01-01T15:00:00Z",
      "body": "I don't know, maybe the configuration. On the server we build with \"CI\", the local build is with \"Debug\".\nHaven't investigated that more in depth, took me a while to figure out why it broke at all. ",
      "reactions": {
        "url": "https://api.github.com/repos/AwesomeAssertions/AwesomeAssertions/issues/comments/3703798555/reactions",
        "total_count": 0,
        "+1": 0,
        "-1": 0,
        "laugh": 0,
        "hooray": 0,
        "confused": 0,
        "heart": 0,
        "rocket": 0,
        "eyes": 0
      },
      "performed_via_github_app": null
    }
  },
  "public": true,
  "created_at": "2026-01-01T15:00:00Z",
  "org": {
    "id": 195190198,
    "login": "AwesomeAssertions",
    "gravatar_id": "",
    "url": "https://api.github.com/orgs/AwesomeAssertions",
    "avatar_url": "https://avatars.githubusercontent.com/u/195190198?"
  }
}