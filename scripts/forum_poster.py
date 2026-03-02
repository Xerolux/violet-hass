#!/usr/bin/env python3
"""
Post release announcements to phpBB forums.
Supports phpBB 3.x forums with login and posting.
"""

import argparse
import re
import sys

import requests


class PhpBBPoster:
    """Handle phpBB forum authentication and posting."""

    def __init__(self, base_url: str, username: str, password: str, timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })

    def login(self) -> bool:
        """Authenticate with the phpBB forum."""
        login_url = f"{self.base_url}/ucp.php?mode=login"
        
        try:
            response = self.session.get(login_url, timeout=self.timeout)
            response.raise_for_status()
            
            sid_match = re.search(r'name="sid"\s+value="([a-f0-9]+)"', response.text)
            sid = sid_match.group(1) if sid_match else ""
            
            creation_time_match = re.search(r'name="creation_time"\s+value="(\d+)"', response.text)
            creation_time = creation_time_match.group(1) if creation_time_match else ""
            
            form_token_match = re.search(r'name="form_token"\s+value="([a-f0-9]+)"', response.text)
            form_token = form_token_match.group(1) if form_token_match else ""
            
            login_data = {
                "username": self.username,
                "password": self.password,
                "login": "Anmelden",
                "redirect": "./index.php",
                "sid": sid,
                "creation_time": creation_time,
                "form_token": form_token,
            }
            
            response = self.session.post(
                login_url,
                data=login_data,
                timeout=self.timeout,
                allow_redirects=True
            )
            response.raise_for_status()
            
            # Check for common logout/sign-out link text in various languages
            logout_indicators = [
                "Abmelden", "Logout", "Log out", "Sign out",
                "Ausloggen", "Déconnexion", "Cerrar sesión",
            ]
            if any(indicator in response.text for indicator in logout_indicators):
                print("Successfully logged in to forum")
                return True

            # Also check if the username appears in the page (another sign of successful login)
            if self.username and self.username.lower() in response.text.lower():
                print("Successfully logged in to forum (username found in response)")
                return True

            # Check that we are no longer on the login page (no login form present)
            if 'name="login"' not in response.text and 'mode=login' not in response.url:
                print("Successfully logged in to forum (login form no longer present)")
                return True

            print("Login may have failed - no successful login indicator found")
            return False
            
        except requests.RequestException as e:
            print(f"Login error: {e}")
            return False

    def get_topic_info(self, topic_id: int) -> dict | None:
        """Get topic information including forum_id for posting."""
        topic_url = f"{self.base_url}/viewtopic.php?t={topic_id}"
        
        try:
            response = self.session.get(topic_url, timeout=self.timeout)
            response.raise_for_status()
            
            forum_match = re.search(r'f=(\d+)', response.text)
            if forum_match:
                return {
                    "topic_id": topic_id,
                    "forum_id": int(forum_match.group(1)),
                    "url": topic_url
                }
            
            return None
            
        except requests.RequestException as e:
            print(f"Error getting topic info: {e}")
            return None

    def post_reply(self, topic_id: int, forum_id: int, message: str) -> bool:
        """Post a reply to an existing topic."""
        posting_url = f"{self.base_url}/posting.php?mode=reply&f={forum_id}&t={topic_id}"
        
        try:
            response = self.session.get(posting_url, timeout=self.timeout)
            response.raise_for_status()
            
            sid_match = re.search(r'name="sid"\s+value="([a-f0-9]+)"', response.text)
            sid = sid_match.group(1) if sid_match else ""
            
            creation_time_match = re.search(r'name="creation_time"\s+value="(\d+)"', response.text)
            creation_time = creation_time_match.group(1) if creation_time_match else ""
            
            form_token_match = re.search(r'name="form_token"\s+value="([a-f0-9]+)"', response.text)
            form_token = form_token_match.group(1) if form_token_match else ""
            
            last_click_match = re.search(r'name="lastclick"\s+value="(\d+)"', response.text)
            last_click = last_click_match.group(1) if last_click_match else ""
            
            post_data = {
                "message": message,
                "subject": "Re: Release Announcement",
                "addbbcode20": "100",
                "post": "Absenden",
                "sid": sid,
                "creation_time": creation_time,
                "form_token": form_token,
                "lastclick": last_click,
                "post_time": creation_time,
                "attach_sig": "on",
                "notify": "on",
            }
            
            response = self.session.post(
                posting_url,
                data=post_data,
                timeout=self.timeout,
                allow_redirects=True
            )
            response.raise_for_status()
            
            if "wurde erfolgreich" in response.text or "successfully" in response.text.lower():
                print("Post successfully submitted!")
                return True
            
            if "viewtopic.php" in response.url:
                print("Post likely successful (redirected to topic)")
                return True
            
            print("Post status unclear - check the forum manually")
            return False
            
        except requests.RequestException as e:
            print(f"Error posting reply: {e}")
            return False


def format_bbcode_release_post(
    version: str,
    tag: str,
    release_type: str,
    release_url: str,
    changelog_url: str,
    download_url: str,
    features: str = "",
    improvements: str = "",
    bugfixes: str = "",
) -> str:
    """Format release announcement as BBCode for phpBB forums."""
    
    type_labels = {
        "stable": ("[color=#008000]✅ STABILE VERSION[/color]", "Stable Release"),
        "alpha": ("[color=#FF0000]🔴 ALPHA VERSION[/color] - Experimentell", "Alpha Release"),
        "beta": ("[color=#FFA500]🟡 BETA VERSION[/color] - Testphase", "Beta Release"),
        "rc": ("[color=#0000FF]🟢 RELEASE CANDIDATE[/color]", "Release Candidate"),
    }
    
    type_label, _ = type_labels.get(release_type, ("[color=#808080]Release[/color]", "Release"))
    
    changelog_section = ""
    if features.strip():
        feature_list = "\n".join(f"[*]{line.strip()}" for line in features.strip().split("\n") if line.strip())
        changelog_section += f"""[quote="[b]✨ Neue Funktionen[/b]"]
[list]
{feature_list}
[/list]
[/quote]

"""
    
    if improvements.strip():
        improvement_list = "\n".join(f"[*]{line.strip()}" for line in improvements.strip().split("\n") if line.strip())
        changelog_section += f"""[quote="[b]🚀 Verbesserungen[/b]"]
[list]
{improvement_list}
[/list]
[/quote]

"""
    
    if bugfixes.strip():
        bugfix_list = "\n".join(f"[*]{line.strip()}" for line in bugfixes.strip().split("\n") if line.strip())
        changelog_section += f"""[quote="[b]🔧 Bug Fixes[/b]"]
[list]
{bugfix_list}
[/list]
[/quote]

"""
    
    post = f"""[b][size=180]🎉 Violet Pool Controller v{version}[/size][/b]

{type_label}

{changelog_section}[quote="[b]📦 Installation[/b]"]
[list=1]
[*][b]HACS (Empfohlen):[/b]
    [list]
    [*]Einstellungen → Geräte & Dienste → Integration hinzufügen
    [*]Nach "Violet Pool Controller" suchen
    [*]Oder Repository [url=https://github.com/Xerolux/violet-hass]Xerolux/violet-hass[/url] als benutzerdefiniertes Repo hinzufügen
    [/list]
[*][b]Manuell:[/b]
    [list]
    [*][url={download_url}]📥 violet_pool_controller.zip[/url] herunterladen
    [*]Nach [c]custom_components/violet_pool_controller[/c] entpacken
    [*]Home Assistant neu starten
    [/list]
[/list]

[size=85]📋 [url={changelog_url}]Vollständiges Changelog auf GitHub[/url] | [url={release_url}]Release Details[/url][/size]
[/quote]

[quote="[b]❤️ Entwicklung unterstützen[/b]"]
Wenn diese Integration nützlich ist, freue ich mich über Unterstützung:
[list]
[*]☕ [url=https://buymeacoffee.com/xerolux]Buy Me a Coffee[/url]
[*]🚗 [url=https://ts.la/sebastian564489]Tesla Referral Code[/url] - Kostenlos für dich, hilfreich für mich
[*]⭐ [url=https://github.com/Xerolux/violet-hass]Repository auf GitHub starren[/url]
[/list]

[i]Jeder Beitrag ist eine große Motivation! Vielen Dank! 🙏[/i]
[/quote]

[quote="[b]💬 Feedback & Hilfe[/b]"]
Bei Fragen oder Problemen gerne im [url=https://github.com/Xerolux/violet-hass/wiki]Wiki[/url] schauen - dort gibt es ausführliche Anleitungen und Tipps.

[list]
[*]🐛 [url=https://github.com/Xerolux/violet-hass/issues/new?template=bug_report.md]Bug melden[/url]
[*]💡 [url=https://github.com/Xerolux/violet-hass/issues/new?template=feature_request.md]Feature wünschen[/url]
[*]📖 [url=https://github.com/Xerolux/violet-hass#readme]Dokumentation auf GitHub[/url]
[/list]
[/quote]

[hr]

[size=85][i]Entwickelt von [url=https://github.com/Xerolux]Xerolux[/url] | [url=https://github.com/Xerolux/violet-hass/blob/main/LICENSE]MIT License[/url] | [url=https://github.com/Xerolux/violet-hass]GitHub[/url][/i][/size]
"""
    
    return post


def main():
    parser = argparse.ArgumentParser(description="Post release to phpBB forum")
    parser.add_argument("--forum-url", required=True, help="Base URL of the phpBB forum")
    parser.add_argument("--username", required=True, help="Forum username")
    parser.add_argument("--password", required=True, help="Forum password")
    parser.add_argument("--topic-id", type=int, required=True, help="Topic ID to reply to")
    parser.add_argument("--version", required=True, help="Release version (e.g., 1.0.3)")
    parser.add_argument("--tag", required=True, help="Release tag (e.g., v1.0.3)")
    parser.add_argument("--release-type", default="stable", help="Release type (stable/alpha/beta/rc)")
    parser.add_argument("--release-url", required=True, help="GitHub release URL")
    parser.add_argument("--changelog-url", required=True, help="Changelog comparison URL")
    parser.add_argument("--download-url", required=True, help="Download URL for ZIP")
    parser.add_argument("--features", default="", help="New features (markdown)")
    parser.add_argument("--improvements", default="", help="Improvements (markdown)")
    parser.add_argument("--bugfixes", default="", help="Bug fixes (markdown)")
    parser.add_argument("--dry-run", action="store_true", help="Print post without submitting")
    parser.add_argument("--timeout", type=int, default=30, help="Request timeout in seconds")
    
    args = parser.parse_args()
    
    message = format_bbcode_release_post(
        version=args.version,
        tag=args.tag,
        release_type=args.release_type,
        release_url=args.release_url,
        changelog_url=args.changelog_url,
        download_url=args.download_url,
        features=args.features,
        improvements=args.improvements,
        bugfixes=args.bugfixes,
    )
    
    if args.dry_run:
        print("=" * 60)
        print("DRY RUN - Post content:")
        print("=" * 60)
        print(message)
        print("=" * 60)
        return 0
    
    poster = PhpBBPoster(
        base_url=args.forum_url,
        username=args.username,
        password=args.password,
        timeout=args.timeout
    )
    
    print(f"Logging in to {args.forum_url}...")
    if not poster.login():
        print("Failed to login to forum")
        return 1
    
    print(f"Getting topic info for topic {args.topic_id}...")
    topic_info = poster.get_topic_info(args.topic_id)
    if not topic_info:
        print("Failed to get topic information")
        return 1
    
    print(f"Posting reply to topic {args.topic_id}...")
    if not poster.post_reply(
        topic_id=topic_info["topic_id"],
        forum_id=topic_info["forum_id"],
        message=message
    ):
        print("Failed to post reply")
        return 1
    
    print("Successfully posted release announcement!")
    print(f"View topic: {topic_info['url']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
