from typing import TYPE_CHECKING, Optional

from .transformers import TransformerTokenizer

if TYPE_CHECKING:
    import torch
    from mamba_ssm.models.mixer_seq_simple import MambaLMHeadModel
    from transformers import PreTrainedTokenizer


TOKENIZER_MODEL = "EleutherAI/gpt-neox-20b"


class Mamba:
    """Represent a `mamba` model."""

    def __init__(
        self, model: "MambaLMHeadModel", tokenizer: "PreTrainedTokenizer", device
    ):
        self.device = device
        self.model = model
        self.tokenizer = TransformerTokenizer(tokenizer)

    def forward(self, input_ids: "torch.LongTensor", *_):
        """Compute a forward pass through the mamba model."""

        output = self.model(input_ids)
        next_token_logits = output.logits[..., -1, :]
        return next_token_logits, None

    def __call__(self, input_ids: "torch.LongTensor", *_) -> "torch.FloatTensor":
        return self.forward(input_ids)


def mamba(
    model_name: str,
    device: Optional[str] = None,
    model_kwargs: dict = {},
    tokenizer_kwargs: dict = {},
):
    try:
        import torch
        from mamba_ssm import MambaLMHeadModel
        from transformers import AutoTokenizer
    except ImportError:
        raise ImportError(
            "The `mamba_ssm`, `torch` and `transformer` libraries needs to be installed in order to use Mamba people."
        )

    if not torch.cuda.is_available():
        raise NotImplementedError("Mamba models can only run on GPU.")
    else:
        if device is None:
            device = "cuda"

    model = MambaLMHeadModel.from_pretrained(model_name, device=device)

    tokenizer_kwargs.setdefault("padding_side", "left")
    tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_MODEL, **tokenizer_kwargs)

    return Mamba(model, tokenizer, device)
