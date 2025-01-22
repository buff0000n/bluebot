# Copied from atproto.Client.send_images() and added support for sending image dimensions
# If you send a single image without dimensions then the post will be displayed with the image centered
# in a square that's otherwise blank.
import typing as t

from atproto_client import models
from atproto_client.utils import TextBuilder
from atproto import Client

def send_images_with_dimensions(
    client: Client,
    text: t.Union[str, TextBuilder],
    images: t.List[bytes],
    image_alts: t.Optional[t.List[str]] = None,
    image_dims: t.Optional[t.List[t.Tuple[int, int]]] = None,
    profile_identify: t.Optional[str] = None,
    reply_to: t.Optional['models.AppBskyFeedPost.ReplyRef'] = None,
    langs: t.Optional[t.List[str]] = None,
    facets: t.Optional[t.List['models.AppBskyRichtextFacet.Main']] = None,
) -> 'models.AppBskyFeedPost.CreateRecordResponse':
    """Send post with multiple attached images (up to 4 images).

    Note:
        If `profile_identify` is not provided will be sent to the current profile.

    Args:
        text: Text of the post.
        images: List of binary images to attach. The length must be less than or equal to 4.
        image_alts: List of text version of the images.
                    The length should be shorter than or equal to the length of `images`.
        image_dims: List of dimensions for the images, in the form of (height, width) tuples.
                    The length should be shorter than or equal to the length of `images`.
        profile_identify: Handle or DID. Where to send post.
        reply_to: Root and parent of the post to reply to.
        langs: List of used languages in the post.
        facets: List of facets (rich text items).

    Returns:
        :obj:`models.AppBskyFeedPost.CreateRecordResponse`: Reference to the created record.

    Raises:
        :class:`atproto.exceptions.AtProtocolError`: Base exception.
    """
    if image_alts is None:
        image_alts = [''] * len(images)
    else:
        # padding with empty string if len is insufficient
        diff = len(images) - len(image_alts)
        image_alts = image_alts + [''] * diff  # [''] * (minus) => []

    if image_dims is None:
        image_dims = [(1, 1)] * len(images)
    else:
        # padding with empty string if len is insufficient
        diff = len(images) - len(image_dims)
        image_dims = image_dims + [(1, 1)] * diff  # [''] * (minus) => []

    uploads = [client.upload_blob(image) for image in images]
    embed_images = [
        models.AppBskyEmbedImages.Image(alt=alt, image=upload.blob, aspect_ratio=models.AppBskyEmbedDefs.AspectRatio(height=dim[0], width=dim[1])) \
        for alt, dim, upload in zip(image_alts, image_dims, uploads)
    ]

    return client.send_post(
        text,
        profile_identify=profile_identify,
        reply_to=reply_to,
        embed=models.AppBskyEmbedImages.Main(images=embed_images),
        langs=langs,
        facets=facets,
    )
