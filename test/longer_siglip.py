import os, torch, torch.nn.functional as F
from transformers import SiglipModel, SiglipProcessor

MODEL_ID = "/home/public/dkx/model/fancyfeast/so400m-long"
NEW_MAX_LEN = 309
SAVE_DIR = "/home/public/dkx/model/fancyfeast/so400m-long-ctx309"

model = SiglipModel.from_pretrained(
    MODEL_ID,
    torch_dtype=torch.float16,
    device_map="auto",
    attn_implementation="sdpa",
)
processor = SiglipProcessor.from_pretrained(MODEL_ID)

old = int(model.config.text_config.max_position_embeddings)
hs  = int(model.config.text_config.hidden_size)
print("old max_position_embeddings =", old, "hidden=", hs)

# --- 扩容并线性插值权重 ---
pos = model.text_model.embeddings.position_embedding  # nn.Embedding(old, hs)

with torch.no_grad():
    w = pos.weight.data.float()                       # [old, hs]
    w3 = w.transpose(0,1).unsqueeze(0)                # [1, hs, old]
    w3_new = F.interpolate(w3, size=NEW_MAX_LEN, mode="linear", align_corners=True)
    w_new = w3_new.squeeze(0).transpose(0,1).contiguous()  # [NEW_MAX_LEN, hs]

    new_pos = torch.nn.Embedding(NEW_MAX_LEN, hs)
    new_pos.weight.data.copy_(w_new)
    new_pos = new_pos.to(dtype=model.dtype, device=pos.weight.device)
    model.text_model.embeddings.position_embedding = new_pos

# --- 同步更新 config（非常关键） ---
model.config.text_config.max_position_embeddings = NEW_MAX_LEN
# 有些实现也会读取根 config 的同名字段，稳妥起见一起写：
setattr(model.config, "max_position_embeddings", NEW_MAX_LEN)

# --- 同步 processor（可选但推荐） ---
if hasattr(processor, "tokenizer"):
    tok = processor.tokenizer
    tok.model_max_length = NEW_MAX_LEN
    if getattr(tok, "pad_token", None) is None:
        tok.pad_token = getattr(tok, "eos_token", None) or tok.add_special_tokens({"pad_token":"<|pad|>"}) or tok.pad_token

# --- 保存：同时保存模型权重 + config + processor ---
os.makedirs(SAVE_DIR, exist_ok=True)
model.save_pretrained(SAVE_DIR)
# 关键：显式把 config 也写盘（有些场景 model.save_pretrained 未覆盖到你改过的嵌套项）
model.config.save_pretrained(SAVE_DIR)
processor.save_pretrained(SAVE_DIR)

print("Saved to:", SAVE_DIR)

# --- 立刻重载验证 ---
test_model = SiglipModel.from_pretrained(
    SAVE_DIR,
    torch_dtype=torch.float16,
    device_map="auto",
    attn_implementation="sdpa",
)
print("reloaded max_position_embeddings =", test_model.config.text_config.max_position_embeddings)
