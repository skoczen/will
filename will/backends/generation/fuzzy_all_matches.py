import logging
import regex
from fuzzywuzzy import fuzz
from fuzzywuzzy import process as fuzz_process
from will import settings
from will.decorators import require_settings
from will.utils import Bunch
from .base import GenerationBackend, GeneratedOption


class FuzzyAllMatchesBackend(GenerationBackend):

    def _generate_compiled_regex(self, method_meta):
        if not hasattr(self, "cached_regex"):
            self.cached_regex = {}

        method_path = method_meta["plugin_info"]["parent_path"]
        if not method_path in self.cached_regex:

            regex_string = method_meta["regex_pattern"]
            if "case_sensitive" in method_meta and not method_meta["case_sensitive"]:
                regex_string = "(?i)%s" % regex_string

            if method_meta["multiline"]:
                try:
                    self.cached_regex[method_path] = regex.compile("%s{e<=%s}" % (
                        regex_string,
                        settings.FUZZY_REGEX_ALLOWABLE_ERRORS
                    ), regex.MULTILINE | regex.DOTALL | regex.ENHANCEMATCH)
                except:
                    self.cached_regex[method_path] = regex.compile("%s{e<=%s}" % (
                        regex.escape(regex_string),
                        settings.FUZZY_REGEX_ALLOWABLE_ERRORS
                    ), regex.MULTILINE | regex.DOTALL | regex.ENHANCEMATCH)
            else:
                try:
                    self.cached_regex[method_path] = regex.compile("%s{e<=%s}" % (
                        regex_string,
                        settings.FUZZY_REGEX_ALLOWABLE_ERRORS
                    ), regex.ENHANCEMATCH)
                except:
                    self.cached_regex[method_path] = regex.compile("%s{e<=%s}" % (
                        regex.escape(regex_string),
                        settings.FUZZY_REGEX_ALLOWABLE_ERRORS
                    ), regex.ENHANCEMATCH)

        return self.cached_regex[method_path]

    def do_generate(self, event):
        exclude_list = ["fn", ]
        matches = []

        message = event.data

        # TODO: add token_sort_ratio
        if message.content:
            if not hasattr(self, "match_choices"):
                self.match_choices = []
                self.match_methods = {}
            for name, l in self.bot.message_listeners.items():
                if not l["regex_pattern"] in self.match_methods:
                    self.match_methods[l["regex_pattern"]] = l
                    self.match_choices.append(l["regex_pattern"])

            search_matches = fuzz_process.extract(message.content, self.match_choices)

            for match_str, confidence in search_matches:
                logging.debug(" Potential (%s) - %s" % (confidence, match_str))
                l = self.match_methods[match_str]
                if (
                        # The search regex matches and
                        # regex_matches

                        # We're confident enough
                        (confidence >= settings.FUZZY_MINIMUM_MATCH_CONFIDENCE)

                        # It's not from me, or this search includes me, and
                        and (
                            message.will_said_it is False or
                            ("include_me" in l and l["include_me"])
                        )

                        # I'm mentioned, or this is an overheard, or we're in a 1-1
                        and (
                            message.is_private_chat or
                            ("direct_mentions_only" not in l or not l["direct_mentions_only"]) or
                            message.is_direct
                        )
                ):
                    logging.info(" Match (%s) - %s" % (confidence, match_str))
                    fuzzy_regex = self._generate_compiled_regex(l)

                    regex_matches = fuzzy_regex.search(message.content)
                    context = Bunch()
                    for k, v in l.items():
                        if k not in exclude_list:
                            context[k] = v
                    if regex_matches and hasattr(regex_matches, "groupdict"):
                        context.search_matches = regex_matches.groupdict()
                    else:
                        context.search_matches = {}

                    o = GeneratedOption(context=context, backend="regex", score=confidence)
                    matches.append(o)

        return matches
