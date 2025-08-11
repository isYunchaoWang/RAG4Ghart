import nltk
import spacy

# nltk.download('punkt')
# nltk.download('maxent_ne_chunker')
# nltk.download('words')
# nltk.download('averaged_perceptron_tagger')


# 正则表达式匹配词（可根据实际需要调整）nltk
# def tokenize(text):
#     tokens = nltk.word_tokenize(text)
#     pos_tags = nltk.pos_tag(tokens)
#     chunks = nltk.ne_chunk(pos_tags)
#
#     result_tokens = []
#     for chunk in chunks:
#         if hasattr(chunk, 'label'):  # 这是命名实体，跳过
#             continue
#         else:
#             result_tokens.append(chunk[0])  # chunk 是 (word, pos)
#
#     return result_tokens

# 加载spaCy的英语模型
nlp = spacy.load("en_core_web_sm")


def tokenize(text):
    # 使用spaCy处理文本
    doc = nlp(text)

    # 存储结果的列表
    result_tokens = []

    # 遍历每个token
    for token in doc:
        # 如果该token不是命名实体，添加到结果列表
        # if not token.ent_type_ and not token.is_stop:
        result_tokens.append(token.lemma_)
        # result_tokens.append(token.text)

    return result_tokens
