import pytest
import json
from RewriteRequest import rewrite_request

class TestRewriteRequest:
    def testRewriteSimple(self):
        rewrite_rules = json.loads(
            """
            [
              { "match": "index.html", "terminate": true },
              { "match": "files/.*", "terminate": true },
              { "match": "post/(?P<year>.+?)/(?P<month>.+?)/(?P<day>.+?)(/.*)?$", "replace": "post.html", "replace_query_string": "year=$<year>&month=$<month>&day=$<day>", "terminate": true },
              { "match": "()(.*)", "replace": "index.html", "replace_query_string": "url=$2", "terminate": true }
            ]
            """
        )

        assert rewrite_request(rewrite_rules, "index.html", "example=true&a=3") == ("index.html", "example=true&a=3", 200)
        assert rewrite_request(rewrite_rules, "files/somefile", "") == ("files/somefile", "", 200)
        assert rewrite_request(rewrite_rules, "otherfile.txt", "a=3") == ("index.html", "url=otherfile.txt", 200)
        assert rewrite_request(rewrite_rules, "post/2018/09/07/post-title", "a=3") == ("post.html", "year=2018&month=09&day=07", 200)

    def testRewriteAdvanced(self):
        rewrite_rules = json.loads(
            """
            [
              { "match": "blog/(.*)", "replace": "index.html", "replace_query_string": "view=$1", "terminate": true },
              { "match": "error/(.*)", "replace": "index.html" },
              { "match": "recursion/(.*)", "replace": "recursion/recursion/$1" },
              { "match_whole": "readme.html\\\\?a=3(.*)", "replace_whole": "index.html?r=5$1", "terminate": true },
              { "match": ".*", "replace": "404.html", "replace_query_string": "url=$0", "terminate": true, "return_code": 404 }
            ]
            """
        )

        assert rewrite_request(rewrite_rules, "index.html", "a=3") == ("404.html", "url=index.html", 404)
        assert rewrite_request(rewrite_rules, "blog/some_page.php", "a=3") == ("index.html", "view=some_page.php", 200)
        assert rewrite_request(rewrite_rules, "recursion/page", "a=3") == ("recursion/page", "a=3", 500)
        assert rewrite_request(rewrite_rules, "error/page", "a=3") == ("404.html", "url=index.html", 404)
        assert rewrite_request(rewrite_rules, "readme.html", "a=3&c=4") == ("index.html", "r=5&c=4", 200)
        assert rewrite_request(rewrite_rules, "readme.html", "a=5&c=4") == ("404.html", "url=readme.html", 404)

    def testRewriteEncodings(self):
        rewrite_rules = json.loads(
            """
            [
              { "match": "encode/(.*)", "replace": "index.html", "replace_query_string": "b64encoded=$B1&urlencoded=$U1", "terminate": true },
              { "match": "decode64/(.*)", "replace": "index.html", "replace_query_string": "b64decoded=$b1", "terminate": true },
              { "match": "urldecode/(.*)", "replace": "index.html", "replace_query_string": "urldecoded=$u1", "terminate": true }
            ]
            """
        )

        assert rewrite_request(rewrite_rules, "encode/hello!", "") == ("index.html", "b64encoded=aGVsbG8h&urlencoded=hello%21", 200)
        assert rewrite_request(rewrite_rules, "decode64/aGVsbG8h", "") == ("index.html", "b64decoded=hello!", 200)
        assert rewrite_request(rewrite_rules, "urldecode/hello%21", "") == ("index.html", "urldecoded=hello!", 200)
        assert rewrite_request(rewrite_rules, "something", "") == ("something", "", 200)
