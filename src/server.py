#!/usr/bin/env python3

"""
Reddit MCP Server using FastMCP

A FastMCP server that provides tools for accessing Reddit's public API.
Supports both local (stdio) and remote (streamable-http) transport modes.
"""

import argparse
from enum import Enum
from datetime import datetime
from typing import Optional

from fastmcp import FastMCP
from pydantic import BaseModel, Field
import redditwarp.SYNC
import redditwarp.models.submission_SYNC


# Initialize FastMCP server with stateless HTTP support for remote deployment
mcp = FastMCP("Reddit MCP Server", stateless_http=True)


# Pydantic Models
class PostType(str, Enum):
    """Types of Reddit posts."""
    LINK = "link"
    TEXT = "text"
    GALLERY = "gallery"
    UNKNOWN = "unknown"


class RedditTools(str, Enum):
    """Available Reddit MCP tools."""
    GET_FRONTPAGE_POSTS = "get_frontpage_posts"
    GET_SUBREDDIT_INFO = "get_subreddit_info"
    GET_SUBREDDIT_HOT_POSTS = "get_subreddit_hot_posts"
    GET_SUBREDDIT_NEW_POSTS = "get_subreddit_new_posts"
    GET_SUBREDDIT_TOP_POSTS = "get_subreddit_top_posts"
    GET_SUBREDDIT_RISING_POSTS = "get_subreddit_rising_posts"
    GET_POST_CONTENT = "get_post_content"
    GET_POST_COMMENTS = "get_post_comments"


class SubredditInfo(BaseModel):
    """Information about a subreddit."""
    name: str
    subscriber_count: int
    description: Optional[str]


class Post(BaseModel):
    """A Reddit post."""
    id: str
    title: str
    author: str
    score: int
    subreddit: str
    url: str
    created_at: str
    comment_count: int
    post_type: PostType
    content: Optional[str]


class Comment(BaseModel):
    """A Reddit comment with recursive replies."""
    id: str
    author: str
    body: str
    score: int
    replies: list['Comment'] = []


class Moderator(BaseModel):
    """A Reddit moderator."""
    name: str


class PostDetail(BaseModel):
    """Detailed post information including comments."""
    post: Post
    comments: list[Comment]


class RedditServer:
    """Reddit API wrapper using redditwarp for accessing Reddit's public API."""
    
    def __init__(self):
        """Initialize Reddit client."""
        self.client = redditwarp.SYNC.Client()
    
    def _get_post_type(self, submission) -> PostType:
        """Determine post type from submission object using redditwarp types."""
        if isinstance(submission, redditwarp.models.submission_SYNC.LinkPost):
            return PostType.LINK
        elif isinstance(submission, redditwarp.models.submission_SYNC.TextPost):
            return PostType.TEXT
        elif isinstance(submission, redditwarp.models.submission_SYNC.GalleryPost):
            return PostType.GALLERY
        return PostType.UNKNOWN
    
    def _get_post_content(self, submission) -> Optional[str]:
        """Extract content from submission based on post type."""
        if isinstance(submission, redditwarp.models.submission_SYNC.LinkPost):
            return submission.permalink
        elif isinstance(submission, redditwarp.models.submission_SYNC.TextPost):
            return submission.body
        elif isinstance(submission, redditwarp.models.submission_SYNC.GalleryPost):
            return str(submission.gallery_link)
        return None
    
    def _build_post(self, submission) -> Post:
        """Convert redditwarp submission to Post model."""
        return Post(
            id=submission.id36,
            title=submission.title,
            author=submission.author_display_name or '[deleted]',
            score=submission.score,
            subreddit=submission.subreddit.name,
            url=submission.permalink,
            created_at=submission.created_at.astimezone().isoformat(),
            comment_count=submission.comment_count,
            post_type=self._get_post_type(submission),
            content=self._get_post_content(submission)
        )
    
    def _build_comment_tree(self, node, depth: int = 3) -> Optional[Comment]:
        """Recursively build comment tree with depth limit."""
        if depth <= 0 or not node:
            return None

        comment = node.value
        replies = []
        for child in node.children:
            child_comment = self._build_comment_tree(child, depth - 1)
            if child_comment:
                replies.append(child_comment)

        return Comment(
            id=comment.id36,
            author=comment.author_display_name or '[deleted]',
            body=comment.body,
            score=comment.score,
            replies=replies
        )
    
    def get_frontpage_posts(self, limit: int = 10) -> list[Post]:
        """Get hot posts from Reddit frontpage."""
        try:
            posts = []
            for subm in self.client.p.front.pull.hot(limit):
                posts.append(self._build_post(subm))
            return posts
        except Exception as e:
            raise ValueError(f"Failed to fetch frontpage posts: {str(e)}")
    
    def get_subreddit_info(self, subreddit_name: str) -> SubredditInfo:
        """Get basic information about a subreddit."""
        try:
            subr = self.client.p.subreddit.fetch_by_name(subreddit_name)
            return SubredditInfo(
                name=subr.name,
                subscriber_count=subr.subscriber_count,
                description=subr.public_description
            )
        except Exception as e:
            raise ValueError(f"Failed to fetch subreddit info for '{subreddit_name}': {str(e)}")
    
    def get_subreddit_hot_posts(self, subreddit_name: str, limit: int = 10) -> list[Post]:
        """Get hot posts from a specific subreddit."""
        try:
            posts = []
            for subm in self.client.p.subreddit.pull.hot(subreddit_name, limit):
                posts.append(self._build_post(subm))
            return posts
        except Exception as e:
            raise ValueError(f"Failed to fetch hot posts from '{subreddit_name}': {str(e)}")
    
    def get_subreddit_new_posts(self, subreddit_name: str, limit: int = 10) -> list[Post]:
        """Get new posts from a specific subreddit."""
        try:
            posts = []
            for subm in self.client.p.subreddit.pull.new(subreddit_name, limit):
                posts.append(self._build_post(subm))
            return posts
        except Exception as e:
            raise ValueError(f"Failed to fetch new posts from '{subreddit_name}': {str(e)}")
    
    def get_subreddit_top_posts(self, subreddit_name: str, limit: int = 10, time: str = "") -> list[Post]:
        """Get top posts from a specific subreddit."""
        try:
            posts = []
            for subm in self.client.p.subreddit.pull.top(subreddit_name, limit, time=time):
                posts.append(self._build_post(subm))
            return posts
        except Exception as e:
            raise ValueError(f"Failed to fetch top posts from '{subreddit_name}': {str(e)}")
    
    def get_subreddit_rising_posts(self, subreddit_name: str, limit: int = 10) -> list[Post]:
        """Get rising posts from a specific subreddit."""
        try:
            posts = []
            for subm in self.client.p.subreddit.pull.rising(subreddit_name, limit):
                posts.append(self._build_post(subm))
            return posts
        except Exception as e:
            raise ValueError(f"Failed to fetch rising posts from '{subreddit_name}': {str(e)}")
    
    def get_post_content(self, post_id: str, comment_limit: int = 10, comment_depth: int = 3) -> PostDetail:
        """Get detailed post content including comments."""
        try:
            submission = self.client.p.submission.fetch(post_id)
            post = self._build_post(submission)
            
            # Fetch comments
            comments = self.get_post_comments(post_id, comment_limit)
            
            return PostDetail(post=post, comments=comments)
        except Exception as e:
            raise ValueError(f"Failed to fetch post content for '{post_id}': {str(e)}")
    
    def get_post_comments(self, post_id: str, limit: int = 10) -> list[Comment]:
        """Get comments from a post."""
        try:
            comments = []
            tree_node = self.client.p.comment_tree.fetch(post_id, sort='top', limit=limit)
            for node in tree_node.children:
                comment = self._build_comment_tree(node)
                if comment:
                    comments.append(comment)
            return comments
        except Exception as e:
            raise ValueError(f"Failed to fetch comments for post '{post_id}': {str(e)}")


# FastMCP Tool Definitions
@mcp.tool()
def get_frontpage_posts(limit: int = Field(default=10, ge=1, le=100)) -> list[dict]:
    """Get hot posts from Reddit frontpage.
    
    Args:
        limit: Number of posts to retrieve (1-100, default 10)
        
    Returns:
        List of frontpage posts with title, author, score, etc.
    """
    reddit_server = RedditServer()
    posts = reddit_server.get_frontpage_posts(limit)
    return [post.model_dump() for post in posts]


@mcp.tool()
def get_subreddit_info(subreddit_name: str) -> dict:
    """Get basic information about a subreddit.
    
    Args:
        subreddit_name: Name of the subreddit (without r/ prefix)
        
    Returns:
        Subreddit information including name, subscriber count, and description
    """
    reddit_server = RedditServer()
    info = reddit_server.get_subreddit_info(subreddit_name)
    return info.model_dump()


@mcp.tool()
def get_subreddit_hot_posts(subreddit_name: str, limit: int = Field(default=10, ge=1, le=100)) -> list[dict]:
    """Get hot posts from a specific subreddit.
    
    Args:
        subreddit_name: Name of the subreddit (without r/ prefix)
        limit: Number of posts to retrieve (1-100, default 10)
        
    Returns:
        List of hot posts from the subreddit
    """
    reddit_server = RedditServer()
    posts = reddit_server.get_subreddit_hot_posts(subreddit_name, limit)
    return [post.model_dump() for post in posts]


@mcp.tool()
def get_subreddit_new_posts(subreddit_name: str, limit: int = Field(default=10, ge=1, le=100)) -> list[dict]:
    """Get new posts from a specific subreddit.
    
    Args:
        subreddit_name: Name of the subreddit (without r/ prefix)
        limit: Number of posts to retrieve (1-100, default 10)
        
    Returns:
        List of new posts from the subreddit
    """
    reddit_server = RedditServer()
    posts = reddit_server.get_subreddit_new_posts(subreddit_name, limit)
    return [post.model_dump() for post in posts]


@mcp.tool()
def get_subreddit_top_posts(
    subreddit_name: str, 
    limit: int = Field(default=10, ge=1, le=100),
    time: str = Field(default="", pattern="^(|hour|day|week|month|year|all)$")
) -> list[dict]:
    """Get top posts from a specific subreddit.
    
    Args:
        subreddit_name: Name of the subreddit (without r/ prefix)
        limit: Number of posts to retrieve (1-100, default 10)
        time: Time window for top posts ("", "hour", "day", "week", "month", "year", "all")
        
    Returns:
        List of top posts from the subreddit
    """
    reddit_server = RedditServer()
    posts = reddit_server.get_subreddit_top_posts(subreddit_name, limit, time)
    return [post.model_dump() for post in posts]


@mcp.tool()
def get_subreddit_rising_posts(subreddit_name: str, limit: int = Field(default=10, ge=1, le=100)) -> list[dict]:
    """Get rising posts from a specific subreddit.
    
    Args:
        subreddit_name: Name of the subreddit (without r/ prefix)
        limit: Number of posts to retrieve (1-100, default 10)
        
    Returns:
        List of rising posts from the subreddit
    """
    reddit_server = RedditServer()
    posts = reddit_server.get_subreddit_rising_posts(subreddit_name, limit)
    return [post.model_dump() for post in posts]


@mcp.tool()
def get_post_content(
    post_id: str,
    comment_limit: int = Field(default=10, ge=1, le=100),
    comment_depth: int = Field(default=3, ge=1, le=10)
) -> dict:
    """Get detailed post content including comments.
    
    Args:
        post_id: Reddit post ID
        comment_limit: Number of top-level comments to retrieve (1-100, default 10)
        comment_depth: Maximum depth of comment replies to fetch (1-10, default 3)
        
    Returns:
        Detailed post information with nested comments
    """
    reddit_server = RedditServer()
    detail = reddit_server.get_post_content(post_id, comment_limit, comment_depth)
    return detail.model_dump()


@mcp.tool()
def get_post_comments(post_id: str, limit: int = Field(default=10, ge=1, le=100)) -> list[dict]:
    """Get comments from a post.
    
    Args:
        post_id: Reddit post ID
        limit: Number of comments to retrieve (1-100, default 10)
        
    Returns:
        List of comments from the post
    """
    reddit_server = RedditServer()
    comments = reddit_server.get_post_comments(post_id, limit)
    return [comment.model_dump() for comment in comments]


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description='Reddit MCP Server using FastMCP')
    parser.add_argument('--port', type=int, default=8081, help='Port for HTTP transport (default: 8081)')
    parser.add_argument('--host', default='127.0.0.1', help='Host for HTTP transport (default: 127.0.0.1)')
    parser.add_argument(
        '--transport', 
        choices=['stdio', 'streamable-http'], 
        default='stdio',
        help='Transport mode: stdio for local, streamable-http for remote (default: stdio)'
    )
    return parser.parse_args()


def main():
    """Main entry point for the Reddit MCP server."""
    args = parse_arguments()
    
    if args.transport == 'streamable-http':
        # Run as HTTP server for remote access
        mcp.run(transport="streamable-http", host=args.host, port=args.port)
    else:
        # Run as stdio server for local access
        mcp.run()


if __name__ == "__main__":
    main()