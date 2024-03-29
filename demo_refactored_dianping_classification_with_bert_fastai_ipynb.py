# -*- coding: utf-8 -*-
"""“demo_refactored_dianping_classification_with_BERT_fastai.ipynb”的副本

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1GDORZ_HLFzya5bZmieiYaqBxeJhBjMSr
"""

from fastai.text import *

!wget https://github.com/wshuyi/public_datasets/raw/master/dianping.csv

df = pd.read_csv("dianping.csv")

from sklearn.model_selection import train_test_split

train, test = train_test_split(df, test_size=.2, random_state=2)

train, valid = train_test_split(train, test_size=.2, random_state=2)

len(train)

len(valid)

len(test)

train.head()

!pip install pytorch-transformers

from pytorch_transformers import BertTokenizer, BertForSequenceClassification

bert_model = "bert-base-chinese"
max_seq_len = 128
batch_size = 32

bert_tokenizer = BertTokenizer.from_pretrained(bert_model)

list(bert_tokenizer.vocab.items())[2000:2005]

bert_vocab = Vocab(list(bert_tokenizer.vocab.keys()))

class BertFastaiTokenizer(BaseTokenizer):
    def __init__(self, tokenizer, max_seq_len=128, **kwargs):
        self.pretrained_tokenizer = tokenizer
        self.max_seq_len = max_seq_len

    def __call__(self, *args, **kwargs):
        return self

    def tokenizer(self, t):
        return ["[CLS]"] + self.pretrained_tokenizer.tokenize(t)[:self.max_seq_len - 2] + ["[SEP]"]

tok_func = BertFastaiTokenizer(bert_tokenizer, max_seq_len=max_seq_len)

bert_fastai_tokenizer = Tokenizer(
    tok_func=tok_func,
    pre_rules = [],
    post_rules = []
)

path = Path(".")

databunch = TextClasDataBunch.from_df(path, train, valid, test,
                  tokenizer=bert_fastai_tokenizer,
                  vocab=bert_vocab,
                  include_bos=False,
                  include_eos=False,
                  text_cols="comment",
                  label_cols='sentiment',
                  bs=batch_size,
                  collate_fn=partial(pad_collate, pad_first=False, pad_idx=0),
             )

databunch.show_batch()

class MyNoTupleModel(BertForSequenceClassification):
  def forward(self, *args, **kwargs):
    return super().forward(*args, **kwargs)[0]

bert_pretrained_model = MyNoTupleModel.from_pretrained(bert_model, num_labels=2)

loss_func = nn.CrossEntropyLoss()

learn = Learner(databunch, 
                bert_pretrained_model,
                loss_func=loss_func,
                metrics=accuracy)

learn.lr_find()

learn.recorder.plot()

learn.fit_one_cycle(2, 2e-5)

def dumb_series_prediction(n):
  preds = []
  for loc in range(n):
    preds.append(int(learn.predict(test.iloc[loc]['comment'])[1]))
  return preds

preds = dumb_series_prediction(len(test))

preds[:10]

from sklearn.metrics import classification_report, confusion_matrix

print(classification_report(test.sentiment, preds))

print(confusion_matrix(test.sentiment, preds))

pdata=learn.predict("设施老化，紧靠马路噪音太大，晚上楼上卫生间的水流声和空调噪音非常大，无法入眠")

print(pdata)

label_denotation = {1:'正向评论',0:'负向评论'}

#标签涵义：1代表正向评论，0代表负向评论
print(label_denotation[int(pdata[1])])

