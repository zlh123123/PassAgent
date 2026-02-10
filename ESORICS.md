# ESORICS投稿与基线对比讨论

## 1. ESORICS投稿与基线对比讨论

**system**: 

```
You are a helpful assistant.
```

**user**: 

```
你看一下这个论文呢，他是25年的ESORICS的，然后我也打算投这个。我做的东西其实差不多和他。我给你传一个我大致的技术报告（并不完整）。然后就是有关基线模型对比这块，我是打算拿着他这里的开源的数据集去重新训一下我的模型，然后再去做评估，你看这样子合理吗？以及哪怕这样子做了我的项目里还有什么欠缺的？
```

Attachments:
- 978-3-032-07894-0_12.pdf
- 基于LLM的口令复用Hashcat规则生成.pdf

**assistant**: 

```


让我先仔细阅读这篇ESORICS论文的完整内容。
```

Tool Call: read_file (state: result)
Args:
  {
    "fileKey": "file:/home/10357289/下载/978-3-032-07894-0_12.pdf-817863-1770607079322",
    "lineOffset": 100,
    "maxLines": 500
  }
Result:
  {
    "fileKey": "file:/home/10357289/下载/978-3-032-07894-0_12.pdf-817863-1770607079322",
    "content": "   101\tthis setting. Pal et  al.  [ \n   102\t16] propose a straightforward round-robin strategy, which \n   103\tapplies a single-leak model (e.g., Pass2Path) to each available leaked password \n   104\tin  turn  and  interleaves  the  resulting  guess  lists.  However,  neither  their  study \n   105\tnor subsequent work has evaluated the practical performance of the round-robin \n   106\tstrategy.  Xiu  and  Wang  [ \n   107\t21]  proposed  MSPointerGuess,  a  multi-leak  password \n   108\tmodel  designed  to  combine  clues  from  multiple  leaked  passwords.  MSPointer-\n   109\tGuess encodes leaked passwords from each website using separate encoders that\n   110\t226F. Huang et al.\n   111\tshare  only  architecture  but  not  parameters,  and  then  employs  a  learnable  soft \n   112\tgate to dynamically determine the information drawn from each source. \n   113\tDespite  these  advancements,  MSPointerGuess  [ 21]  faces  significant  limita-\n   114\ttions. In multi-leak settings, the number of leaked passwords for each user and \n   115\ttheir source websites vary widely. Consequently, requiring a distinct encoder for \n   116\teach leaked password severely hinders the model’s scalability. Even with shared \n   117\tencoder  architecture,  this  design  implies  a  rigid  model  structure  that  must  be \n   118\tspecifically  tailored  or  trained  for  each  distinct  number  of  leaked  passwords  a \n   119\tuser  possesses.  This  makes  it  poorly  adaptable  to  the  wide  variability  in  leak \n   120\tcounts observed in real-world scenarios, thereby limiting its practical applicabil-\n   121\tity and effectiveness. \n   122\tOur  Contributions \n   123\tIn  this  paper,  we  focus  on  multi-leak  scenarios  and  aim  to  build  a  probability \n   124\tmodel  that  accurately  captures  the  similarity  among  multiple  passwords  from \n   125\tthe same user for password guessing. \n   126\tWe  propose  Pass2Pass-T,  a  Transformer-based  [ 19]  password  probability \n   127\tmodel, for predicting a target password from one or multiple leaked passwords \n   128\tof the same user. Fundamentally, it operates by concatenating leaked passwords \n   129\tinto a single sequence which is then fed into the Transformer for guess genera-\n   130\ttion. Recognizing that these concatenated password sequences differ from natural \n   131\tlanguage in three key aspects: their semi-structured nature, high repetitiveness, \n   132\tand lack of typical syntax, we introduce several adaptations. First, we refine the \n   133\tpositional encoding by introducing a segment-wise scheme tailored to password \n   134\tsequences.  For  data  augmentation,  we  also  apply  epoch-level  random  shuffling \n   135\tof  leaked  passwords.  Second,  departing  from  common  tokenization  techniques, \n   136\twe  propose  a  repetition-aware  compression  scheme  to  represent  the  relation-\n   137\tships  among  leaked  passwords  more  clearly  and  concisely.  Finally,  we  leverage \n   138\ttransfer  learning  by  pre-training  on  extensive  single-leak  data  and  fine-tuning \n   139\ton comparatively smaller multi-leak data. \n   140\tWe evaluate existing models under single-leak and multi-leak scenarios. \n   141\tIn the single-leak  scenario, where the attacker holds exactly one leaked pass-\n   142\tword per user, our method achieves a 4.46% attack-success advantage over the \n   143\tbest models at the 10\n   144\t7\n   145\t-guess mark. \n   146\tIn the multi-leak  scenario, where the attacker has access to multiple leaked \n   147\tpasswords per user, our method surpasses previous state-of-the-art methods: it \n   148\tcompromises  4.87%  of  user  accounts  on  the  first  guess—a  7.27×  improvement \n   149\tover the best prior multi-leak attack—and breaks 16.36% of accounts within the \n   150\tfirst five guesses, a 58.9% relative gain. We provide the first systematic empirical \n   151\tevaluation  of  round-robin  guessing,  comparing  it  directly  with  our  multi-leak \n   152\tmodel. \n   153\tTo summarize, we mainly have the following contributions. \n   154\t– We  focus  on  multi-leak  scenarios,  propose  Pass2Pass-T,  to  predict  a  target \n   155\tpassword based on several leaked passwords from the same user. Our model\n   156\tPersonalized Password Guessing227\n   157\tmainly leverage Transformer and enhances it with input compression and seg-\n   158\tmented  positional  encoding,  tailored  to  the  distinct  characteristics  of  pass-\n   159\tword sequences unlike natural language texts. \n   160\t– We  evaluate  Pass2Pass-T  and  show  it  outperforms  existing  attacks  in  both \n   161\tmulti-leak scenarios and single-leak scenarios. \n   162\t– Our multi-similarity model adapts to an arbitrary number of leak passwords, \n   163\twhereas MSPointerGuess requires training and testing on a fixed number of \n   164\tleak passwords. \n   165\t2  Related  Work \n   166\t2.1  Password  Reuse  Behaviors \n   167\tDue to cognitive limitations, users frequently reuse or only slightly modify pass-\n   168\twords across different online services. Florencio and Herley [ \n   169\t5] first documented \n   170\tthe widespread prevalence of password reuse and weak passwords in a large-scale \n   171\tuser  study  in  2007;  later,  Das et  al.  [ \n   172\t4]  corroborated  these  findings  using  web-\n   173\tsite  data  at  NDSS’14.  Subsequent  studies,  such  as  Pearman et  al.  [ \n   174\t18],  found \n   175\tthat  passwords  containing  special  characters  or  numbers  are  more  likely  to  be \n   176\treused. These findings highlight the persistent and multifaceted nature of pass-\n   177\tword reuse. \n   178\t2.2  Personalized  Password  Guessing  via  Leaked  Passwords \n   179\tAttackers can exploit users’ habit of reusing or slightly modifying existing pass-\n   180\twords  across  different  websites.  In  2019,  Pal  et  al.  [ \n   181\t16]proposed Pass2Path, \n   182\ta  sequence-to-sequence  model  that  converts  old  passwords  into  sequences  of \n   183\tcharacter-level edits, cracking nearly 48% of accounts within 1,000 guesses. How-\n   184\tever,  it  cannot  capture  the  mutual  influence  among  edit  operations  and  the \n   185\ttransformation  effects  they  produce,  nor  can  it  leverage  popular  password  dic-\n   186\ttionaries.  At  USENIX  Security  2023,  Wang  et  al.  [ \n   187\t20]  introduced  Pass2Edit, \n   188\twhich breaks password transformation into multi-step classification, improving \n   189\tsuccess rates by 43%  over Pass2Path  in the first 100  guesses for  normal  users, \n   190\tand by another 24% when adding a global dictionary. Yet both Pass2Edit  and \n   191\tPass2Path  only perform single-character edits and remove dissimilar pairs dur-\n   192\ting training, limiting their ability to model long-range transformations. In 2024, \n   193\tXiu  and  Wang  [ \n   194\t21]proposed PointerGuess,  which  builds  on  Bahdanau  et  al.’s \n   195\tattention  mechanism  [ \n   196\t1]  and  Long  Short-Term  Memory  (LSTM)  networks  [ 8], \n   197\tand uses a pointer network to jointly model copying old characters and generat-\n   198\ting new ones, supporting both personalized and population-level reuse behaviors \n   199\twithout  external dictionaries,  and further extended it to multi-leak  settings  as \n   200\tMSPointerGuess.\n   201\t228F. Huang et al.\n   202\t3  Multi-leak  Password-Guessing  Attack \n   203\tIn this section, we introduce the data processing methods and analyze the pass-\n   204\tword reuse behavior and characteristics of passwords across multiple accounts. \n   205\tBased on this analysis, we propose our model, Pass2Pass-T. \n   206\t3.1  Dataset  Collection  and  Pre-Processing \n   207\tWe use the RMDC email aggregation dataset as multi-leak data. Originally, it \n   208\twas a password vault dataset covering aggregated data from 28 sites, with each \n   209\tuser having a different number of leaks. \n   210\tTerminology.    This paper directly employs the RMDC dataset that is released \n   211\tin work [ \n   212\t2]. To familiarise readers with its properties, we briefly summarise the \n   213\tmain cleaning steps below. \n   214\tData  Source  and  Preprocessing.    The raw RMDC archive (182 sites, about \n   215\t427GB)  was  collected  from  public  hacker  forums.  We  keep  only  28  plain-text \n   216\tdump  files  and  apply  three  sequential  filters:  (i)  remove  passwords  containing \n   217\tnon-printable  ASCII  characters;  (ii)  retain  entries  whose  user-name  length  is \n   218\t≥ 3 and password length is 4–25; (iii) require the e-mail field to contain the “@” \n   219\tsymbol. \n   220\tAggregation  Strategy.    After  cleaning,  they  aggregate  accounts  by  e-mail \n   221\taddress  rather  than  user  name.  This  prevents  extremely  common  user  names \n   222\t(e.g. “abc”) from merging passwords belonging to different individuals into the \n   223\tsame  vault,  which  would  otherwise  contaminate  cross-user  data.  Although  e-\n   224\tmail aggregation can occasionally split a single user’s credentials across multiple \n   225\tvaults,  its  impact  on  subsequent  evaluation  is  smaller  than  that  of  user-name \n   226\taggregation. \n   227\tFull  details  can  be  found  in  the  paper  [ 2].  The  dataset  and  preprocessing \n   228\tscripts are available at \n   229\thttps://zenodo.org/records/15646753. \n   230\t1\n   231\t3.2  Password  Reuse  Behaviors \n   232\tBeyond the single-password–reuse behavior noted in prior work [ 16,20], there are \n   233\talso significant or potential relationships between multiple passwords of a user. \n   234\tWe show examples of these relationships in Table \n   235\t1. For some passwords, users \n   236\tsimply reuse strings from different previous passwords. For example, in Exam-\n   237\tple 1, “xslfly” and “512” come from “xslfly118” and “1990512” respectively. In \n   238\taddition to direct password reuse, there is also latent information between mul-\n   239\ttiple passwords. For instance, in Example 7, “B4cp7eii” and “Bcpeiim” exhibit \n   240\ta corresponding relationship. \n   241\tAdditionally,  passwords  from  the  same  user  are  often  highly  repetitive  and \n   242\tsyntax-free. As shown in Examples 3 and 4, strings like “1995622” and “282026” \n   243\tappear  repeatedly  within  the  passwords.  In  Examples  2  and  8,  even  though \n   244\tpasswords like “B4cp7eii” and “Bcpeiim”, as well as “mar1na” and “mari”, are \n   245\tsimilar, they exhibit flexibility in their expression.\n   246\t1 \n   247\tthe dataset requires an ethics-compliance application \n   248\tPersonalized Password Guessing229\n   249\tTable  1.  Typical examples of similarity among multiple passwords \n   250\tReuse TypeNo. Leak passwordTarget \n   251\tPassword segment concatenation 11990512xslfly11819905121990512xslfly512 \n   252\t2mar1nabill1950chick1968 mari03mar1na03 \n   253\t3199562219956221995622dengbinjunjun1995622 \n   254\t4denglei1112 282026282026282026deng282026 \n   255\tConsidering users’ reuse habits56sasha6sasha66sasha00022 sasha666500022sasha \n   256\t6131192Julio92juliojulio100julio100 \n   257\t7mamzeljaMamzelja7f074b7F074b47f074b4 \n   258\t8B4cp7eiiBcpeiim1910 eleon1910 1910Bcpeiim B4cp7eiim \n   259\tNote:  All  displayed  passwords  have  been  anonymized  and  rewritten  to  protect  user \n   260\tprivacy. \n   261\t3.3  Multi-password  Model \n   262\tWe made some simple adaptations to password data based on Transformer [ 19] \n   263\tand  constructed  the  Pass2Pass-T  model,  which  is  a  multi-leakage  password \n   264\tmodel. The choice of Transformer is due to its prominence in natural language \n   265\tprocessing, where password generation can be seen as a character-level language \n   266\tmodeling task, and Transformer is the mainstream model for this task. For the \n   267\tmulti-leak  scenario,  we  concatenate  all  leaked  passwords  of  the  same  account \n   268\twith <sep>  into  a  single  sequence,  compress  it  with  a  dedicated  strategy,  and \n   269\temploy  a  decoder-only  Transformer   [ \n   270\t19]  for  autoregressive  modeling  to  fully \n   271\texploit its long-context capacity and high training throughput. We adapted to \n   272\tthe data characteristics of multiple password sequences. \n   273\tInput  Data  Handling  Strategies.  We considered three processing methods, \n   274\tof which the first two have already been tried in password processing, while the \n   275\tthird is a new strategy we propose. \n   276\t1) BPE  subword  segmentation: BPE subword segmentation is a mainstream app-\n   277\troach in NLP. However, passwords are morphologically diverse, and the same \n   278\tsemantic fragment may appear in many spellings (e.g., p@ssword, Pa55word, \n   279\tp4w0rd),  yielding  non-unique  tokenization  paths  and  unstable  Monte-Carlo \n   280\testimates at high guess ranks. \n   281\t2) Keyboard-mapping:  Following  Pass2Edit  /  Pass2Path,  each  character  is \n   282\tmapped  to  its  US-keyboard  coordinate  to  shorten  edit  sequences.  This \n   283\tchiefly benefits edit-distance models (e.g., transforming abcdefg  to ABCDEFG \n   284\tneeds only one <CAP>  insertion). Our experiments show negligible impact on \n   285\tcharacter-level generators. \n   286\t3) Repetition-aware  compression: When the current password is identical to any \n   287\tprevious  one in the same account, we replace the entire string with a pointer \n   288\tsymbol  <s \n   289\tj>,  where j  denotes  the  position  of  its  first   occurrence  in  the \n   290\tsequence. For example, if the 3rd password repeats the 1st, we encode it as \n   291\t<s \n   292\t1>.  This  compression  shortens  the  input  and  improves  performance,  so\n   293\t230F. Huang et al.\n   294\tPass2Pass-T  adopts  it.  Under  credential-stuffing  defenses,  repetition-aware \n   295\tcompression markedly boosts top-5 success rates (see Table \n   296\t5). \n   297\tSegment-Wise  Positional  Encoding.  The vanilla sinusoidal positional encod-\n   298\ting presumes a globally monotonically increasing index, which multi-leak inputs \n   299\tobviously  violate.  We  therefore  reset  the  positional  index  at  every  password \n   300\tboundary  and  append  a  one-hot  segment  tag  to  avoid  spurious  inductive  bias. \n   301\tConcretely,  within  each  password  we  keep  the  original  Transformer  sin–cos \n   302\tencoding,  while  across  passwords  we  add  a  one-hot  vector  to  distinguish  seg-\n   303\tments,  as  illustrated  in  Fig. \n   304\t2.  During  training,  we  randomly  shuffle  the  order \n   305\tof  password  blocks  at  the  epoch  level  to  weaken  the  model’s  dependence  on  a \n   306\tpseudo-timeline. \n   307\tFig.  2.  Segment Level embedding \n   308\tPre-training.  A large corpus of single-password samples enhances brute-force \n   309\tcapacity; we pre-train on it and fine-tune on multi-password data, enabling the \n   310\tmodel to learn cross-password similarities. \n   311\tIn sum, by combining repetition-aware compression, segment-wise positional \n   312\tencoding, and pre-training, Pass2Pass-T captures multi-password reuse patterns \n   313\tmore accurately. \n   314\t3.4  Monte-Carlo  PPSM \n   315\tWe propose to pre-sample password-similarity trajectories offline so that a newly \n   316\tentered  password  could  be  scored  with  a single  forward  pass.  While  attractive \n   317\tfor small candidate sets on compute-rich devices, the overall cost would still scale \n   318\tas O(n\n   319\t2\n   320\t) with the number n  of stored passwords, and quantifying this trade-off \n   321\tis left for future experiments. \n   322\t4  Empirical  Evaluation \n   323\tWe  evaluate  our  model  in  two  single-leak  attack  scenarios  and  six  multi-leak \n   324\tattack scenarios (when the number of given passwords is one, our model auto-\n   325\tmatically  degenerates  to  the  single-leak  model,  so  we  include  that  scenario  as \n   326\twell). Next, we assess the performance of our similarity model under high guess \n   327\tcounts to reflect the threat of offline attacks, which prior work has not revealed. \n   328\tFinally,  we  perform  ablation  studies  to  demonstrate  the  contribution  of  each \n   329\tcomponent to the model’s performance.\n   330\tPersonalized Password Guessing231\n   331\t4.1  Experimental  Setting \n   332\tFor the multi-similar experiment settings, We chose RMDC because we regard \n   333\tMSPointerGuess’s multi-leak setting as unrealistic: their attacker knows at most \n   334\ttwo historical passwords per user, both taken from only two identical datasets. \n   335\tTherefore, their setting diverges sharply from real-world conditions—where the \n   336\tnumber of leak passwords per user varies and originates from diverse sites—and \n   337\tcannot faithfully reflect the true threat landscape. \n   338\tWe  follow  the  experimental  setup  of  Pass2Path  [ 16].  We  evaluate  the \n   339\tattacker’s  capabilities  when  they  know  different  numbers  of  passwords,  under \n   340\ttwo  conditions:  one  where  direct  reuse  of  leak  passwords  is  removed  (referred \n   341\tto as  “no repeat” hereafter) and  one  where  it is  not . Additionally,  we  set dif-\n   342\tferent  numbers  of  leak  passwords  for  the  attacker  to  reflect  the  impact  of  leak \n   343\tpasswords on the success rate of account compromise. \n   344\tFor  the  multi-leak  experiments  we  use  the  RMDC  dataset  and  adopt  the \n   345\tPass2Path [ \n   346\t16] evaluation protocol. We vary the number of leak passwords avail-\n   347\table to the attacker  and compare their  success against  two site configurations: \n   348\twith and without credential-stuffing protection. \n   349\tSpecifically,  we  use  the  other  passwords  to  predict  the  final  password.  To \n   350\tcontrol input length, we truncate each record to the first six passwords. The last \n   351\tpassword  in  the  truncated  list  is  used  as  the  attack  target,  and  the  preceding \n   352\tentries serve as leak inputs. \n   353\tIn  this  chapter,  we  use Leak  Num  to  denote  the  number  of  passwords  the \n   354\tattacker possesses. \n   355\t– ≥ 1  scenario—keep the original RMDC distribution and treat the last pass-\n   356\tword of each account as the prediction target. \n   357\t– ≥ 2  scenario—select  accounts  with 3–6   passwords,  using  the  first n−1to \n   358\tpredict the n-th. \n   359\t– =5 scenario—select  accounts  with 6–10   leaked  passwords  and  retain  the \n   360\tfirst six (i.e., five leak plus one to predict). \n   361\tThe  “≥ 1”  bucket  preserves the dataset’s  natural  distribution,  whereas the \n   362\t“≥  2”  and  “=  5”  buckets  simulate  moderate  and  severe  leakage  conditions, \n   363\trespectively, enabling us to evaluate attack accuracy under different leakage lev-\n   364\tels. \n   365\tWe  used  the  RMDC  open-source  7  million  data,  with  90%  as  the  training \n   366\tset, and the remaining 10% was filtered using the method mentioned earlier to \n   367\textract 10,000 samples from each of the 6 scenarios for testing. \n   368\tHyperparameter  Settings.  For our model, we configured the model dimensions to \n   369\t512, employed 8 attention heads and 8 layers, set a dropout rate of 0.1, limited \n   370\tthe  maximum  sequence  length  to  128  tokens,  used  a  training  set  ratio  of  0.95, \n   371\ttrained for 15 epochs, and applied gradient accumulation with 2 steps. We used \n   372\ta batch size of 128. This arrangement was chosen because the loss had essentially \n   373\tconverged by the 15th epoch. \n   374\tRegarding the training strategy, we adopted a learning rate of 1e-4, a warmup \n   375\tof 1000, and a cosine annealing learning rate.\n   376\t232F. Huang et al.\n   377\tFor  the  Pass2Edit \n   378\t2\n   379\tand  Pass2Path  models,  we  follow  the  original  data \n   380\tpipeline and train on the similar password pairs. \n   381\t3\n   382\tIn terms of pair count, our new \n   383\tdataset  is  comparable  to  4iQ.  Since  we  observed  that  validation  loss  continues \n   384\tto decrease beyond three epochs, for a fair comparison we also train Pass2Edit \n   385\tfor 15 epochs and save the checkpoint with the lowest validation loss. \n   386\tFor  our  model,  we  pre-trained  for  1.5  days  on  two  RTX  3090  GPUs  (using \n   387\t10% of the merged single-password dataset) and then fine-tuned for 0.6 days on \n   388\ta single RTX 3090. \n   389\t4.2  Ethical  Considerations \n   390\tThis  dataset  has  been  widely  disseminated  through  BitTorrent  (BT).  In  our \n   391\tstudy, it is used solely to advance password protection technologies rather than \n   392\tto inflict further harm. \n   393\tWe treat each password as confidential during processing; no real user pass-\n   394\twords  appear  in  this  paper,  and  all  displayed  passwords  are  edited  variants  of \n   395\tthe  originals.  Access  to  the  data  is  restricted  to  the  participants  of  this  study, \n   396\tand authentication via certificates is required. \n   397\t4.3  Estimation  for  Crack  Rate \n   398\tThe optimal strategy for password guessing is: to  strictly  attempt  all  candidate  pass-\n   399\twords in descending order of model probability. However, sampling probabilities that \n   400\tstrictly decrease monotonically from the model is impractical, so estimation meth-\n   401\tods are needed. We use Beam Search and Monte Carlo methods for evaluation. \n   402\tBeamSearch  explicitly enumerates and attacks the k  = 1 000 highest-probability \n   403\tpasswords  generated  by  the  model.  It  has  been  adopted  in  prior  work  such  as \n   404\tPass2Path, Pass2Edit, and PointerGuess [ \n   405\t16,20,21]. Its exhaustive nature, how-\n   406\tever, makes evaluation at very large guess budgets computationally prohibitive. \n   407\tMonte  Carlo  is a statistical estimator that samples passwords from the model \n   408\tand  applies  inverse-probability  weighting,  yielding  an  unbiased  estimate  of  the \n   409\tcrack rate even at extremely high guess counts. \n   410\t4.4  Experimental  Results  in  Multi-leak  Attack  Scenarios \n   411\tWe first employed Beam Search to evaluate performance with a low number of \n   412\tguesses.  We  observed  that,  under  such  conditions,  our  model  exhibits  a  signif-\n   413\ticant  improvement  in  accuracy  within  the  first  100  attempts—particularly  on\n   414\t2 \n   415\tPass2Edit [\n   416\t20] was not open-sourced, we reimplemented the method described in the \n   417\tpaper.  We  evaluated  our  implementation  under  the  original  authors’  experimental \n   418\tScenario 1; the results are shown in Table \n   419\t2. Our reproduction yields results approx-\n   420\timately  1%  higher  than  those  reported  in  the  original  work,  with  the  discrepancy \n   421\twithin an acceptable margin, indicating that the reproduction is essentially accurate. \n   422\t3 \n   423\tIn the previous paper, approximately 116 million password pairs from the 4iQ dataset \n   424\twere  used  for  training.  Applying  the  Pass2Edit  filtering  algorithm  to  10%  of  that \n   425\tdata produced 112 million pairs. \n   426\tPersonalized Password Guessing233\n   427\tTable  2.  Crack Rate in Multi-Leak Scenarios \n   428\tLeak \n   429\tnum \n   430\tGuess \n   431\tnum \n   432\tFLA  [\n   433\t12\n   434\t] \n   435\tPass2Edit \n   436\t[\n   437\t20\n   438\t] \n   439\tPass2Path \n   440\t[\n   441\t16\n   442\t] \n   443\tPointerGuess \n   444\tTransformer \n   445\tPass2Pass-\n   446\tT \n   447\t≥ 1 \n   448\t12.59%43.51%43.51%46.26%47.03%47.23% \n   449\t52.98%55.65%55.23%56.32%57.41%57.61% \n   450\t103.68%56.95%56.29%57.47%58.68%58.91% \n   451\t1005.94%60.29%58.22%60.72%61.88%62.00% \n   452\t10008.44%63.26%59.61%62.88%64.37%64.67% \n   453\t10\n   454\t7 \n   455\t40.49%\\\\76.27%79.25%79.40% \n   456\t≥ 2 \n   457\t12.76%49.11%48.34%54.38%55.34%55.95% \n   458\t53.20%67.18%67.84%68.25%69.65%69.81% \n   459\t103.79%68.65%69.08%69.62%71.09%71.27% \n   460\t1006.12%72.07%71.14%72.72%73.96%74.02% \n   461\t10008.76%74.94%72.40%74.81%76.02%76.18% \n   462\t10\n   463\t7 \n   464\t41.30%\\\\83.65%85.95%86.43% \n   465\t=5 \n   466\t13.25%45.03%45.13%57.02%58.50%59.70% \n   467\t54.11%74.60%76.98%76.02%78.58%78.89% \n   468\t104.76%77.00%78.90%78.21%80.63%80.84% \n   469\t1007.12%80.81%81.09%81.87%83.17%83.29% \n   470\t10009.65%83.58%82.09%83.48%84.35%84.43% \n   471\t10\n   472\t7 \n   473\t37.42%\\\\88.68%89.80%89.96% \n   474\t≥ 1 \n   475\t(no \n   476\trepeat) \n   477\t12.17%0.73%0.61%1.00%1.08%1.27% \n   478\t52.95%11.08%7.87%10.82%12.38%12.74% \n   479\t103.16%13.12%9.88%12.99%15.01%15.34% \n   480\t1004.90%18.61%13.95%19.07%21.08%21.40% \n   481\t10007.34%23.83%16.51%23.45%26.19%26.71% \n   482\t10\n   483\t7 \n   484\t36.94%\\\\49.89%   56.99%56.84% \n   485\t≥ 2 \n   486\t(no \n   487\trepeat) \n   488\t12.67%0.18%0.23%0.69%1.12%1.98% \n   489\t53.18%10.92%7.27%9.76%12.75%13.48% \n   490\t103.67%14.19%10.96%13.49%17.00%17.49% \n   491\t1005.89%21.82%16.71%22.07%24.93%25.39% \n   492\t10008.47%27.90%20.52%27.16%30.54%31.21% \n   493\t10\n   494\t7 \n   495\t38.84%\\\\53.03%59.87%60.48% \n   496\t=5 \n   497\t(no \n   498\trepeat) \n   499\t12.93%0.18%0.24%0.67%2.02%4.87% \n   500\t53.92%9.64%4.95%8.39%13.58%16.36% \n   501\t104.28%15.84%12.38%13.57%21.02%21.99% \n   502\t1007.21%25.95%21.54%26.02%31.54%32.01% \n   503\t10009.93%33.49%26.52%32.59%36.49%36.93% \n   504\t10\n   505\t7 \n   506\t39.44%\\\\53.35%58.70%59.33% \n   507\tNote:   Bolded  entries  indicate  the  best-performing  model  when  attacking \n   508\tbased on leaked passwords. \n   509\t234F. Huang et al. \n   510\t(a) Leak  Num1(b) Leak  Num2(c) Leak  Num  =  5 \n   511\tFig.  3. Attack Success Rate within the Top 1,000 Guesses on the Repeat Multi-Leak \n   512\tAttack Scenarios \n   513\t(a) Leak  Num1(b) Leak  Num2\n   514\t(c) Leak  Num  =  5 \n   515\tFig.  4. Attack Success Rate within the Top 1,000 Guesses on the No-Repeat Multi-\n   516\tLeak Attack Scenarios \n   517\tthe very first guess. The results are shown in Figs. 4, 3, and Table 2.Onthe very \n   518\tfirst guess, our method cracked 4.87% of accounts, revealing that round-robin \n   519\tattacks severely underestimate an attacker’s early-stage cracking power. \n   520\tIn the repeat scenario, when attackers possess more than five Leak passwords, \n   521\tour\n   522\t method—compared to the best previous approach—increases the first-guess \n   523\tsuccess rate from 57.02% to 59.70%. In the no-repeat scenario, the success rate \n   524\timproves from 0.67% to 4.87%, representing a 7.27-fold increase. \n   525\tWe observe that although PointerGuess is the most recent model, its actual \n   526\tattac\n   527\tk performance in multi-leak scenarios is worse than that of the round-robin-\n   528\tbased Pass2Edit. We speculate that this performance gap stems from the archi-\n   529\ttectural design of PointerGuess, which first generates multiple separate password \n   530\tdistributions and only combines them at the final stage. As a result, interactions \n   531\tbetween different Leak passwords occur too late in the process, making it difficult \n   532\tfor the model to capture cross-password dependencies effectively. \n   533\tIn addition, we find it achieves better first-guess accuracy than its round-\n   534\trobin\n   535\t variant but loses this advantage by the 10th guess, indicating limited gen-\n   536\teralization (see Appendix B for details). \n   537\tOur analysis reveal that, compared to our multi-leak model, the single-leak \n   538\tmo\n   539\tdel tends to directly reuse passwords on the first attempt (unlike Pass2Edit, \n   540\twhere we did not force the first guess to be a reuse; otherwise, the first-guess \n   541\tsuccess rate would be zero) due to the lack of additional user information. In \n   542\tPersonalized Password Guessing235 \n   543\tcontrast, our multi-leak model enables the attacker can infer the user’s password \n   544\thabits, whether they tend to reuse passwords or make slight modifications. \n   545\t4.5  Result  Analyze \n   546\tTable  3. Comparison examples of single-leak and multi-leak attacks: top 5 and top \n   547\t31–40 \n   548\tLeak \n   549\tpw\n   550\tgurgled123 \n   551\tsparkie123 \n   552\thouxiaochao \n   553\txiaochao521 \n   554\tB4cp7eii \n   555\tBcpeiim1910 \n   556\t191991 \n   557\teleon1910 \n   558\t1910Bcpeiim \n   559\tTargetsalle123houxiaochao521173232 \n   560\tRankPass2EditOursPass2EditOursPass2EditOurs \n   561\t1gurgled123sparkie123houxiaochao xiaochao521B4cp7eiiB4cp7eiim \n   562\t2\n   563\tsparkie123gurgled123xiaochao521 houxiaochaoBcpeiim1910B4cp7eii \n   564\t3\n   565\tgurgledgurgled123456xiaochao191991b4cp7eii \n   566\t4\n   567\tsparkiesparkiexiaochao52xiaochao52eleon1910eleon1910 \n   568\t5\n   569\tgurgled1sparkie12houxiaochao1 houxiaochao521 1910bcpeiimEleon1910 \n   570\t... \n   571\t31gurgled23gurgled13163.comhouxiao5211910acpeiEleon191 \n   572\t32\n   573\tsparkie2123gurgledhouchaoxiaochao521.Acp7eii19191991 \n   574\t33\n   575\tgurgled12345 neopets123a123456houxiaochao019911991Bcpeiim191 \n   576\t34\n   577\tsparkie14love1231314521xiaochao521521eleon10123456 \n   578\t35\n   579\tGurgledspark12313145205201314a1cp7eii1991Eleon \n   580\t36\n   581\tsparkie12345 dragon123woainiXiaochao521BCPEIIM1910 B4cp7eiim1910 \n   582\t37\n   583\tsparkie01sparkie12345 houda7758521111111191910 \n   584\t38\n   585\tgurgled14princess123 xiaochao521. woainiB4cp7eii4cp7eiim \n   586\t39\n   587\tSparkiesparkie101houxiaochao2 houxiaochaBcpeiim191eleon1991 \n   588\t40\n   589\tgurgled2gurgled22chao521hdchao521191991a1991bcpeiim \n   590\tFor our example, we selected the Pass2Edit + round-robin scheme—shown to achieve \n   591\tthe best empirical attack performance among earlier methods—rather than the more \n   592\trecent MSPointerGuess. \n   593\tIn the no-repeat scenario, with 100 guesses and five leak passwords, our multi-\n   594\tleak model still delivers an improvement of nearly 5.99% in success rate, which \n   595\tis 23.02% higher compared to Pass2Edit. As presented in Table 3, for select data \n   596\tsamples\n   597\t with such improvements, we examined both the first five attack attempts \n   598\tand the list of attacks from the 31st to the 40th guesses. \n   599\tWe found that our multi-leak model can capture the intrinsic relationships \n   600\tamong",
    "lineOffset": 100,
    "linesRead": 500,
    "totalLines": 955
  }

Tool Call: read_file (state: result)
Args:
  {
    "fileKey": "file:/home/10357289/下载/978-3-032-07894-0_12.pdf-817863-1770607079322",
    "lineOffset": 600,
    "maxLines": 355
  }
Result:
  {
    "fileKey": "file:/home/10357289/下载/978-3-032-07894-0_12.pdf-817863-1770607079322",
    "content": "   601\t samples to launch more precise attacks. For instance, when “gurgled123” \n   602\tand “sparkie123” are leak passwords, the single-leak plus round-robin method \n   603\ttypically generates numerous variants of “gurgled” and “sparkie”—as observed \n   604\tin the 31st to 40th guesses—whereas our multi-leak model identifies common \n   605\tpatterns across the passwords, attempting to break the password pair using \n   606\t236F. Huang et al. \n   607\t(a) Leak  Num1(b) Leak  Num2\n   608\t(c) Leak  Num  =  5 \n   609\tFig.  5. Comparative experiments with the state-of-the-art no-leak attack FLA under \n   610\tthe no-repeat scenario \n   611\tstrategies such as combining an English word with “123”. In the second example, \n   612\ta simpler cross-password reuse is observed by concatenating “521” from the \n   613\tleak passwords “houxiaochao” and “xiaochao521”, which allowed our multi-leak \n   614\tmodel to break the password in just 5 guesses. \n   615\tIn the third example, where a greater number of leak passwords are available, \n   616\tthe\n   617\t model deduced the target password on the very first guess. It inferred that \n   618\tthe relation between “Bcpeiim” and “B4cp7eiim” involves the insertion of two \n   619\tdigits within “Bcpeiim”, and, taking into account previous accounts suggesting \n   620\tthat users might avoid directly reusing passwords, it opted for a combination \n   621\tstrategy. \n   622\t4.6  Advantage  of  Multi-Leak  Attacks  Under  High  Guess  Numbers \n   623\tWe refer to attacks that do not rely on leaked passwords as no-leak  attacks. \n   624\tIn\n   625\t previous research, only Pass2Path compared single-leak  attacks and no-leak \n   626\tattacks. Since it did not consider non-similar passwords, their experimental \n   627\tresults showed that after 100,000 guesses, the single-leak attack had no advan-\n   628\ttage over the no-leak attack. \n   629\tIn contrast, our model, during training, learns from less similar password \n   630\tpairs.\n   631\t Using the Monte Carlo method for evaluation, we found, contrary to previ-\n   632\tous conclusions, that under almost all guess numbers, the performance of no-leak \n   633\tattacks is worse than that of multi-leak attacks. \n   634\tWe find that the primary advantage comes from samples that exhibit partial \n   635\tsimilarit\n   636\ty combined with enumerative patterns. In such cases, the model can \n   637\tleverage partial similarity information to achieve orders-of-magnitude improve-\n   638\tments in attack success rates. See Table 4. \n   639\tSince Pass2Edit and Pass2Path are edit-based—where a single password cor-\n   640\tresp\n   641\tonds to multiple generation paths and accurate probability computation is \n   642\tinfeasible—we did not include them in the high-guess-count evaluation (Fig. 5). \n   643\tPersonalized Password Guessing237 \n   644\tTable  4. Attack Results of Different Methods on Two Target Passwords \n   645\tTarget \n   646\tpw \n   647\tzq534126514fadednegro33 \n   648\tMethodFLA [12] Pass2Pass-T Pass2Pass-T FLA [12] Pass2Pass-T Pass2Pass-T \n   649\tLeak \n   650\tpw \n   651\t\\\\wangqi890519 \\\\domything33 \n   652\tRank8.48e+11 4.78e+119.60e+93.84e+14 4.51e+132.10e+12 \n   653\tTable  5. Ablation experiment results (percentage) \n   654\tGuess \n   655\tnum \n   656\tPass2Pass-T \n   657\t(Transformer \n   658\t+zip \n   659\tpw \n   660\t+new \n   661\tpos finetune) \n   662\tTransformer \n   663\t+zip \n   664\tpw \n   665\tTransformer Transformer \n   666\tsspm \n   667\tPass2Edit \n   668\t[\n   669\t20] \n   670\tAblation \n   671\tVariants \n   672\torgABCD \n   673\tLeak Num =5 and no repeat \n   674\t14.87%4.22%2.02%0.22%0.18% \n   675\t516.36%15.25%13.58%6.80%9.64% \n   676\t1021.99%20.64%21.02%17.37%15.84% \n   677\t10032.01%31.50%31.54%29.90%25.95% \n   678\t100036.93%36.72%36.49%35.53%33.49% \n   679\t4.7  Ablation  Study \n   680\tIn order to validate the impact of the methods proposed in this paper, we \n   681\tdesigned\n   682\t a series of ablation experiments. Specifically, based on the complete \n   683\tmodel, we individually removed the following key factors, as shown in Table 5: \n   684\tA) Removal of the new positional encoding and pretraining strategy; \n   685\tB) Disabling the compression strategy; \n   686\tC) Replacing the multi-leak method with standard round-robin; \n   687\tD) Replacing the Transformer module with the Pass2Edit model. \n   688\t4.8  Single-Leak  Scenario  Evaluation \n   689\tIn addition to the multi-leak scenario, we have also evaluated the model’s per-\n   690\tformance\n   691\t under the single-leak scenario. \n   692\tWe conduct two single-leak experiments. Setting A trains on Tianya → \n   693\tDo\n   694\tdonew and is evaluated on Tianya → Taobao. Setting B setup uses 90% \n   695\tof the 7 million data from the RMDC dataset for training, and the remaining \n   696\tportion is filtered to test the cases where Leak  Num = 1 (Table 6). \n   697\t238F. Huang et al. \n   698\tTable  6. Comparison of Results (%) on Two Datasets \n   699\tLeak Num Guess num Pass2Edit [20] PointerGuess [21] Pass2Pass-T \n   700\tSetting  A:  Tianya→Dodonew  (train);  Tianya→Taobao  (test) \n   701\t=1127.28%27.73%26.94% \n   702\t531.10%31.10%31.24% \n   703\t1032.15%31.99%32.26% \n   704\t10034.09%34.20%34.33% \n   705\t100036.40%36.27%36.58% \n   706\t10\n   707\t7 \n   708\t–50.14%52.38% \n   709\tSetting  B:  RMDC  7M  (train);  RMDC  100K  (test) \n   710\t=1140.42%40.21%40.64% \n   711\t546.88%47.05%48.05% \n   712\t1048.19%47.92%49.23% \n   713\t10051.13%51.45%52.41% \n   714\t100053.94%53.55%55.42% \n   715\tUsing the same training and testing setup as Scenario 1 in Pass2Edit—Tianya \n   716\t→ Dodonew for training and Tianya → Taobao for testing—we conduct a fair \n   717\tcomparison between the prior method and ours. We observe no significant per-\n   718\tformance difference, indicating that the previous approach is already sufficient \n   719\tto capture single-password modification patterns within 1,000 guesses. \n   720\t5  Conclusion \n   721\tWe focus on multi-leak scenarios and propose Pass2Pass-T to predict a target \n   722\tpassword from several leaked passwords of the same user. Pass2Pass-T leverages \n   723\tthe Transformer, enhanced with input compression and segmented positional \n   724\tencoding tailored to passwords. This design enables Pass2Pass-T to outperform \n   725\texisting methods in both single-leak and multi-leak scenarios. Additionally, we \n   726\tintroduce a password strength estimator based on Monte Carlo methods, helping \n   727\tusers select appropriate passwords in multi-leak situations. \n   728\tAcknowledgment. This research is supported by National Natural Science Founda-\n   729\ttion of China (No. 62202012 and No. 62072010), BIGC Project Ea202515 and Pub-\n   730\tlishing Think Tank Platform Development Project KYCPT202514. We also thank the \n   731\tanonymous reviewers for their valuable comments and suggestions. \n   732\tPersonalized Password Guessing239 \n   733\tAppendix \n   734\tA  MSPointerGuess  Implement \n   735\tIn the original PointerGuess formulation [ 21], several implementation details \n   736\tare left unspecified, which undermines reproducibility. To address this, we now \n   737\tpresent a complete account of our multi-source PointerGuess implementation. \n   738\tWe noticed an inconsistency in the PointerGuess paper between the calcula-\n   739\ttion\n   740\t of Pg in Eq. 5 and its depiction in Fig. 3. Therefore, we follow the method \n   741\tin\n   742\t Eq. 5 when computing Pg. \n   743\tSecond, although MSPointerGuess defines a multi-source fusion mechanism \n   744\tfor\n   745\t the copy distribution P\n   746\tcopy\n   747\t, it omits any description of how the generation \n   748\tdistribution P\n   749\tvocab \n   750\tis obtained. To fill this gap, we compute individual context \n   751\tvectors C \n   752\t(i) \n   753\tt \n   754\tfor each leaked password, weight each vector by its learned soft-gate \n   755\tscore, and sum them to form a global context C\n   756\tt\n   757\t. We then concatenate C\n   758\tt \n   759\twith \n   760\tthe decoder state s\n   761\tt \n   762\tand project the result to produce P\n   763\tvocab\n   764\t. \n   765\tThird, we observe that Eq. (5) applies two successive linear mappings with-\n   766\tout\n   767\t intervening non-linearities; since such mappings can be algebraically merged \n   768\tinto a single affine transformation, we implement this step using a single fully \n   769\tconnected layer. \n   770\tFinally, We observe that in the original MSPointerGuess design, the number \n   771\tof\n   772\t projection matrices W\n   773\tc \n   774\tequals the number of leak passwords, giving a one-\n   775\tto-one correspondence between each W\n   776\tc \n   777\tand its context vector C\n   778\tt \n   779\t(see Eq. 9 in \n   780\tthe MSPointerGuess paper). In our setting, however, every sample contains a \n   781\tvariable number of leak passwords and the websites are shuffled, so no position \n   782\tconveys extra information. Hence, we train a single global W\n   783\tc \n   784\tto project all C\n   785\tt \n   786\tvectors and reuse the same encoder to encode each password multiple times. \n   787\tB  Comparison  Between  Simple  Round-Robin \n   788\tand  MSPointerGuess  Approaches \n   789\tWe compare three strategies whose results are summarized in Table 7: \n   790\t1. Original  MSPointerGuess: feed the entire set of leak passwords for a user \n   791\tat\n   792\t once; the model computes probabilities for all candidates in a shared con-\n   793\ttext and guesses in descending order of these scores. \n   794\t2. Round-robin: run MSPointerGuess separately on each leak-password \n   795\tsequence,\n   796\t take the current top-scoring candidate from every sequence in turn, \n   797\tand remove duplicates. \n   798\t3. Global  sort: also compute probabilities separately for each sequence, but \n   799\tpoo\n   800\tl all candidates and sort them globally by probability before guessing. \n   801\tIn the leak-num = 5 setting, MSPointerGuess (MSPG) outperforms round-\n   802\trobin\n   803\t in one-guess (top-1) accuracy. However, its performance degrades signifi-\n   804\tcantly under the leak-num = 5 (no-repeat) condition. \n   805\t240F. Huang et al. \n   806\tTable  7. Crack rates of three guessing strategies on the RMDC dataset (percentage) \n   807\tLeak \n   808\tnum \n   809\tGuess \n   810\tnum \n   811\tRound-\n   812\trobin \n   813\t(dedup) \n   814\tGlobal \n   815\tsort\n   816\t \n   817\tMS-\n   818\tPointerGuess \n   819\t≥ 1143.38%43.11%46.26% \n   820\t555.12%56.48%56.32% \n   821\t1056.34%57.70%57.47% \n   822\t100062.76%62.85%62.88% \n   823\t=5144.68%44.76%57.02% \n   824\t571.95%76.83%76.02% \n   825\t1074.21%78.97%78.21% \n   826\t100082.82%83.37%83.48% \n   827\t≥ 1 \n   828\t(no  repeat) \n   829\t10.85%0.87%1.00% \n   830\t510.91%10.93%10.82% \n   831\t1012.83%13.11%12.99% \n   832\t100023.29%23.31%23.45% \n   833\t=5 \n   834\t(no  repeat) \n   835\t10.07%0.21%0.67% \n   836\t57.57%5.61%8.39% \n   837\t1012.21%13.54%13.57% \n   838\t100031.57%32.32%32.59% \n   839\tTo further investigate this phenomenon, we compare the distribution of target \n   840\tpassword repetition rates between the two methods for their first-guess advan-\n   841\ttage samples (i.e., samples where MSPG ranks the correct password higher than \n   842\tround-robin) under the leak-num = 5 setting. The results are shown in Fig. 6: \n   843\t(a) The target password repetition rates of MSPG’s first-guess advantage \n   844\tsamples;\n   845\t \n   846\t(b) The target password repetition rates of the leak-num = 5 test set; \n   847\t(c) The target password repetition rates of the leak-num = 5 (no-repeat) test \n   848\tset.\n   849\t \n   850\tIt can be observed that MSPG’s advantage mainly comes from cases where \n   851\tthe\n   852\t target password appears multiple times in the leak set. When the target \n   853\tpasswords are non-repeating, as in (c), its top-1 success rate drops significantly. \n   854\tThis indicates that MSPG lacks generalization ability under multi-password con-\n   855\tditions with non-repetitive targets. \n   856\tThis limited effectiveness likely results from its origins as a lightweight (0.5 M-\n   857\tparameter)\n   858\t extension of the PointerGuess model, which was originally designed \n   859\tfor single-leak scenarios and thus struggles to capture correlations across multiple \n   860\tleaked passwords. \n   861\tPersonalized Password Guessing241 \n   862\t(a) MSPointerGuess’s \n   863\tfirst  guess  advantage \n   864\tsamples \n   865\t(b) the  leak-num  =  5 \n   866\ttest  set \n   867\t(c) the  leak-num  =  5 \n   868\t(no-repeat)  test  set \n   869\tFig.  6. Target password repetition rate distributions under the leak-num = 5 setting \n   870\tC  Impact  of  the  Estimation  Method \n   871\tMC is slightly more optimistic because it avoids beam-search pruning, as theory \n   872\tpredicts (Table 8). \n   873\tTable  8. Crack rate comparison between Transformer and Pass2Pass-T under different \n   874\testimation methods (percentage form) \n   875\tGuess num Monte Carlo ↑Beam Search ↑ \n   876\tTransformer Pass2Pass-T Transformer Pass2Pass-T \n   877\t1021.09%23.10%21.02%21.99% \n   878\t10031.58%32.39%31.54%32.01% \n   879\t100036.88%37.52%36.49%36.93% \n   880\tReferences \n   881\t1. Bahdanau, D., Cho, K., Bengio, Y.: Neural machine translation by jointly learning \n   882\tto align and translate. In: Proceedings of the International Conference on Learning \n   883\tRepresentations (ICLR) (2015) \n   884\t2. Cheng, H., Huang, F., Yang, J., Li, W., Wang, P.: Practically secure honey pass-\n   885\tw\n   886\tord vaults: new design and new evaluation against online guessing. In: Proceed-\n   887\tings of the 34th USENIX Security Symposium (USENIX Security) (2025) \n   888\t3. Cor, K., Sood, G.: Pwned: How often are Americans’ online accounts breached? \n   889\tarXiv\n   890\t preprint arXiv:1808.01883 (2018) \n   891\t4. Das, A., Bonneau, J., Caesar, M., Borisov, N., Wang, X.F.: The tangled web of \n   892\tpassw\n   893\tord reuse. In: Proceedings of the 21st USENIX Security Symposium (NDSS \n   894\t’14), San Diego, CA, USA (2014) \n   895\t242F. Huang et al. \n   896\t5. Florencio, D., Herley, C.: A large-scale study of web password habits. In: Proceed-\n   897\tings\n   898\t of the 16th International Conference on World Wide Web, WWW ’07, pp. \n   899\t657–666, New York, NY, USA. Association for Computing Machinery (2007) \n   900\t6. Ghorbani Lyastani, S., Schilling, M., Neumayr, M., Backes, M., Bugiel, S.: Is fido2 \n   901\tthe\n   902\t kingslayer of user authentication? A comparative usability study of fido2 pass-\n   903\twordless authentication. In: 2020 IEEE Symposium on Security and Privacy (SP), \n   904\tpp. 268–285 (2020) \n   905\t7. Hanamsagar, A., Woo, S.S., Kanich, C., Mirkovic, J.: Leveraging semantic trans-\n   906\tformation\n   907\t to investigate password habits and their causes. In: Proceedings of the \n   908\t2018 CHI Conference on Human Factors in Computing Systems, CHI ’18, pp. 1–12, \n   909\tNew York, NY, USA. Association for Computing Machinery (2018) \n   910\t8. Hochreiter, S., Schmidhuber, J.: Long short-term memory. Neural Comput. 9(8), \n   911\t1735–1780\n   912\t (1997) \n   913\t9. Hunt, T.: Have I been pwned (2025). https://haveibeenpwned.com \n   914\t10. Ma, J., Yang, W., Luo, M., Li, N.: A study of probabilistic password models. In: \n   915\tIEEE\n   916\t S&P 2014, pp. 538–552 (2014) \n   917\t11. Mainka, C., Mladenov, V., Schwenk, J., Wich, T.: Sok: single sign-on security — an \n   918\tev\n   919\taluation of OpenID connect. In: 2017 IEEE European Symposium on Security \n   920\tand Privacy (EuroS&P), pp. 251–266 (2017) \n   921\t12. Melicher, W., et al.: Fast, lean, and accurate: modeling password guessability using \n   922\tneural\n   923\t networks. In: USENIX Security 2016, pp. 175–191 (2016) \n   924\t13. Negi, P., Sharma, P., Jain, V., Bahmani, B.: K-means++ vs. behavioral biometrics: \n   925\tone\n   926\t loop to rule them all (2018) \n   927\t14. Nicholas, M.: 68 million reasons why your small business needs a password man-\n   928\tager.\n   929\t Dashlane Blog (2017). https://blog.dashlane.com/68-million-reasons-why-\n   930\tyour-small-business-needs-a-password-manager/ \n   931\t15. NordPass: How many passwords does the average person have? Average user holds \n   932\t168\n   933\t personal and 87 work passwords (2024) \n   934\t16. Pal, B., Daniel, T., Chatterjee, R., Ristenpart, T.: Beyond credential stuffing: \n   935\tpassw\n   936\tord similarity models using neural networks. In: 2019 IEEE Symposium on \n   937\tSecurity and Privacy (SP), pp. 417–434 (2019) \n   938\t17. Pasquini, D., Ateniese, G., Troncoso, C.: Universal neural-cracking-machines: self-\n   939\tconfigurable\n   940\t password models from auxiliary data. In: IEEE S&P 2024, pp. 1365– \n   941\t1384, Los Alamitos, CA, USA, May 2024. IEEE Computer Society (2024) \n   942\t18. Pearman, S., et al.: Let’s go in for a closer look: observing passwords in their natural \n   943\thabitat.\n   944\t In: Proceedings of the 2017 ACM SIGSAC Conference on Computer and \n   945\tCommunications Security, CCS ’17, pp. 295–310, New York, NY, USA. Association \n   946\tfor Computing Machinery (2017) \n   947\t19. Vaswani, A., et al.: Attention is all you need. In: NIPS 2017, vol. 30 (2017) \n   948\t20. Wang, D., Zou, Y., Xiao, Y.-A., Ma, S., Chen, X.: Pass2Edit: a multi-step genera-\n   949\ttiv\n   950\te model for guessing edited passwords. In: 32nd USENIX Security Symposium \n   951\t(USENIX Security 23), pp. 983–1000, Anaheim, CA, August 2023. USENIX Asso-\n   952\tciation (2023) \n   953\t21. Xiu, K., Wang, D.: PointerGuess: targeted password guessing model using pointer \n   954\tmechanism. In: 33rd USENIX Security Symposium (USENIX Security 24), pp. \n   955\t5555–5572, Philadelphia, PA, August 2024. USENIX Association (2024) ",
    "lineOffset": 600,
    "linesRead": 355,
    "totalLines": 955
  }

```


好的，我已经仔细阅读了这篇ESORICS 2025论文（Pass2Pass-T）和你的技术报告。下面我来做一个系统性的对比分析，并回答你的问题。

---

## 一、两篇工作的核心对比

| 维度 | Pass2Pass-T (ESORICS 2025) | 你的工作 |
|------|---------------------------|---------|
| **核心思路** | 用Transformer直接从多个泄露密码**生成**目标密码（seq2seq，字符级） | 用LLM微调来**生成Hashcat规则**，再用规则变换旧密码得到新密码 |
| **模型** | 从头训练的小型decoder-only Transformer（512维，8层8头） | 微调Qwen3-1.7B（现成LLM + DoRA/LoRA） |
| **输出空间** | 直接输出密码字符序列 | 输出Hashcat规则序列（如`sab`, `$1`, `[`等） |
| **多泄露场景** | ✅ 核心贡献，支持任意数量泄露密码 | ❌ 目前仅处理单对密码（旧→新） |
| **数据集** | RMDC（28站聚合，700万用户，按邮箱关联） | 6个泄露库，223万用户，按邮箱关联 |
| **规则提取** | 不涉及规则，直接端到端生成 | A*算法逆向构造Hashcat规则（~90%准确率） |
| **评估指标** | Crack Rate @ k guesses（k=1,5,10,100,1000,10^7） | Top-k Hit Rate（规则命中率） |
| **基线对比** | Pass2Edit, Pass2Path, PointerGuess, MSPointerGuess, FLA | 仅Frequency Top-10 和 Hashcat Best66 |

---

## 二、关于你的方案：用他们的开源数据集重新训练你的模型做对比

**这个思路是合理的，但需要注意以下几点：**

### ✅ 合理之处
1. **数据集统一**：用同一个RMDC数据集训练和测试，可以做到公平对比，这是审稿人最看重的。
2. **他们已开源**：论文明确说数据集在 `zenodo.org/records/15646753`（需伦理申请），有预处理脚本。
3. **可复现基线**：他们的Pass2Pass-T以及Pass2Edit、Pass2Path的结果都有详细数字，你可以直接引用。

### ⚠️ 需要注意的问题

1. **评估指标必须对齐**：你目前的评估是"Top-k Hit Rate"（规则是否命中），但Pass2Pass-T用的是**Crack Rate @ k guesses**（在k次猜测内破解的账户比例）。这两个指标**不是同一个东西**。你需要：
   - 把你的模型生成的规则**实际应用到旧密码上**，生成候选密码列表
   - 然后按概率排序，计算在k次猜测内的破解率
   - 这样才能和他们的Table 2直接对比

2. **猜测预算的公平性**：你的模型生成Top-200规则，每条规则作用于一个旧密码产生一个候选，所以最多200个猜测。但Pass2Pass-T评估到了10^7次猜测。你需要考虑如何扩展猜测空间。

3. **多泄露场景是他们的核心卖点**：你目前只处理单对密码（一个旧→一个新），而他们的核心贡献是**多个泄露密码联合预测**。如果你只在single-leak场景对比，那你的对比范围会很窄（只能对标他们Table 6的Setting B部分）。

---

## 三、你的项目目前的主要欠缺

### 🔴 关键欠缺（投稿前必须解决）

**1. 缺乏与学术SOTA的对比**
- 你目前只对比了Frequency Top-10和Hashcat Best66，这两个都是非常弱的基线。
- **必须加入**：Pass2Edit、Pass2Path、PointerGuess 至少其中两个作为基线。Pass2Path有开源代码，Pass2Edit他们也做了复现。
- 审稿人一定会问："为什么不和现有的密码猜测模型比？"

**2. 评估指标不够标准**
- 密码安全领域的标准评估是 **Crack Rate vs. Guess Number 曲线**（即在给定猜测次数下能破解多少比例的账户）。
- 你的"Top-k Hit Rate"更像是一个中间指标（规则层面的准确率），不是最终的安全评估指标。
- 需要做端到端评估：旧密码 → 生成规则 → 应用规则得到候选密码 → 与真实新密码比对 → 计算破解率。

**3. 缺少多泄露场景**
- 这是当前领域的热点（Pass2Pass-T的核心贡献就是这个）。
- 你的LLM方法理论上可以扩展：把多个旧密码都放进prompt里，让模型综合考虑生成规则。
- 如果不做多泄露，你的工作在novelty上会弱很多。

**4. 缺少与端到端生成方法的本质区别论证**
- 你需要回答一个核心问题：**为什么要生成规则而不是直接生成密码？**
- 可能的优势：
  - 规则可解释性强（安全分析师可以理解攻击模式）
  - 规则可以与Hashcat等工具链集成，实际部署更方便
  - 规则具有迁移性（同一规则可应用于不同密码）
  - 规则空间比密码空间小，学习效率更高
- 这些需要用实验数据来支撑。

### 🟡 中等欠缺（建议补充）

**5. 缺少跨数据集泛化实验**
- Pass2Pass-T做了Setting A（Tianya→Dodonew训练，Tianya→Taobao测试），这是跨站泛化。
- 你也应该做类似实验：在一组数据集上训练，在另一组上测试。

**6. 缺少高猜测次数下的评估**
- Pass2Pass-T用Monte Carlo方法评估到了10^7次猜测。
- 你需要考虑如何在大猜测预算下评估你的方法（比如组合多条规则、结合字典等）。

**7. 缺少与no-leak攻击的对比**
- Pass2Pass-T对比了FLA（一个不依赖泄露密码的纯统计模型），证明了泄露密码的价值。
- 你也应该加入类似的baseline。

**8. 规则提取的局限性分析不足**
- 你的A*算法准确率约90%，那10%失败的case是什么？对模型训练有什么影响？
- 你的数据清洗去掉了位置相关的规则（中间位置的插入i和覆写o），这会丢失多少信息？

### 🟢 锦上添花

**9. 安全应用场景**
- Pass2Pass-T提出了Monte-Carlo PPSM（密码强度评估器）。
- 你可以考虑你的规则生成方法在防御端的应用（比如检测用户新密码是否可以通过简单规则从旧密码推导出来）。

**10. LLM的独特优势展示**
- 既然用了LLM，可以展示一些LLM特有的能力，比如：
  - Zero-shot/Few-shot能力（不微调直接让LLM生成规则）
  - 对不同语言/文化背景密码的适应性
  - Prompt engineering的灵活性

---

## 四、具体建议的实验计划

如果你要投ESORICS（或同级别会议），建议按以下优先级补充：

1. **【最高优先】** 在RMDC数据集上，用Crack Rate @ k guesses指标，与Pass2Edit、PointerGuess、Pass2Pass-T做single-leak对比
2. **【高优先】** 扩展你的方法到multi-leak场景（多个旧密码→规则生成）
3. **【高优先】** 明确论证"生成规则 vs 直接生成密码"的优劣，用实验数据支撑
4. **【中优先】** 跨数据集泛化实验
5. **【中优先】** 高猜测次数评估（Monte Carlo或其他方法）
6. **【中优先】** 消融实验更系统化（你已有一些，但需要更完整）

---

## 五、总结

你的方向（用LLM生成Hashcat规则）和Pass2Pass-T（用Transformer直接生成密码）是**互补而非完全重叠**的。你的独特卖点在于：
- **可解释性**：规则比直接生成的密码更可解释
- **工具链集成**：直接输出Hashcat规则，可以和现有渗透测试工具无缝对接
- **LLM的泛化能力**：利用预训练LLM的知识

但要投顶会，**基线对比的深度和广度**是你目前最大的短板。用他们的数据集重新训练是正确的第一步，但评估指标、对比方法、场景覆盖都需要大幅加强。
```

**user**: 

```
是这样，就是因为pass2edit、pointerguess这两个模型没有开源的代码，所以我复现很困难，所以才打算用他这里已经有的数据。这样子会不会让审稿人觉得我工作量不够？ 我有点担心这个
扩展你的方法到multi-leak场景？那对于我输入的多个口令，输出的规则作用在谁上？
我反而认为那种一对多的反而是没有人做过的。

明确论证"生成规则 vs 直接生成密码"的优劣：这个的论证可以从哪几个层面去做？

Zero-shot/Few-shot能力、Prompt engineering的灵活性如何体现？

对不同语言/文化背景密码的适应性？这个什么意思？我在中文的数据集上训练去英文上测试吗
```

**assistant**: 

```


你提出的这些问题都非常好，说明你在认真思考研究的定位。让我逐一回答：

---

## 一、关于复现困难和直接引用他们的数据

**这完全合理，不会让审稿人觉得工作量不够。** 学术界对此有成熟的惯例：

1. **直接引用原论文的数字**：你可以在论文里写"We directly cite the results reported in [Pass2Pass-T] since they use the same dataset and evaluation protocol"。这在安全顶会里非常常见。
2. **关键前提**：你必须确保你的评估设置（数据集划分、猜测预算、评估指标）和他们**完全一致**。如果你用了他们的RMDC数据集，并且按照他们的Setting A/B划分，那直接引用他们Table里Pass2Edit、PointerGuess的数字是完全可以的。
3. **审稿人真正在意的不是你有没有自己跑基线**，而是对比是否公平、是否充分。如果你自己跑了一个不公平的对比，反而更糟。

**但你需要额外做一件事**：至少自己实现一个简单的基线（比如Pass2Edit的核心思想是编辑距离操作，你可以实现一个简化版），证明你理解这些方法。或者用他们开源的Pass2Pass-T代码跑一下你自己的数据集，做双向验证。

---

## 二、关于Multi-leak场景和"一对多"

你说得对，这里需要仔细想清楚。你提出的"一对多"思路其实很有意思，让我帮你梳理一下：

### Pass2Pass-T的multi-leak（多对一）

输入：password1, password2, password3, password4, password5（同一用户的5个泄露密码）
输出：target_password（目标密码）


### 你的场景下multi-leak如果照搬（多对一）

输入：password1, password2, password3
输出：规则？→ 作用在谁身上？

你说得对——**这里有一个天然的矛盾**：规则是针对某一个具体输入的变换，多个输入密码各不相同，一条规则不可能同时适用于所有输入。

### 你提出的"一对多"思路（这才是你的差异化方向！）


输入：一个泄露密码 "zhangsan123"
输出：多条规则 → 生成多个候选密码
  规则1: $4 → "zhangsan1234"
  规则2: s31 → "zhangsan121" 
  规则3: ] $! → "zhangsan12!"
  ...


**这个方向确实没有人系统做过，而且非常有实际价值：**

- Pass2Edit/PointerGuess/Pass2Pass-T 都是给定一个（或多个）旧密码，生成一个候选密码，要生成多个候选就要多次采样
- 你的方法天然可以**一次性输出多条规则**，每条规则都是一个独立的猜测策略
- 而且规则之间有**概率排序**（LLM输出的概率），可以按优先级尝试

**这可以作为你论文的一个核心卖点**：

> "Unlike existing password-to-password models that generate one candidate at a time, our rule-based approach generates a ranked list of transformation rules in a single inference pass, each representing a distinct guessing strategy."

### 更进一步：multi-leak下你也可以做

思路是**分别对每个泄露密码生成规则，然后融合**：


泄露密码1: "zhangsan123" → 规则集A: {$4, s31, ]$!}
泄露密码2: "zs123456"   → 规则集B: {s64, $7, sa@}
泄露密码3: "zhangsan!"  → 规则集C: {$1$2$3, s!@}

融合策略：
- 对所有规则按LLM输出概率统一排序
- 或者：如果多个密码生成了相似的规则模式（比如都倾向于在末尾加数字），提升这类规则的优先级


这种方式既利用了多个泄露密码的信息，又保持了规则的可解释性。

---

## 三、"生成规则 vs 直接生成密码"的论证

这是你论文最核心的motivation之一，可以从以下几个层面论证：

### 层面1：可解释性（Interpretability）
- **实验方法**：展示你模型输出的Top-10规则，让人一眼就能看出用户的密码修改习惯
- 比如："用户倾向于在末尾递增数字（$1→$2）、替换特殊字符（s!@）"
- Pass2Pass-T直接输出密码，你无法知道它"为什么"猜这个密码
- **应用价值**：安全管理员可以根据规则分布制定密码策略（比如禁止仅修改末尾数字）

### 层面2：组合泛化性（Compositional Generalization）
- **这是最强的实验论证点**
- 规则是**与具体密码解耦的**：规则`$1`可以作用于任何密码
- 实验设计：
  - 在数据集A上训练，学到规则分布
  - 在数据集B上测试，密码完全不同，但规则仍然适用
  - 对比Pass2Pass-T在同样跨数据集场景下的性能衰减
- 预期结果：你的方法在跨数据集泛化时衰减更小，因为规则空间比密码空间稳定得多

### 层面3：工具链集成（Practical Deployment）
- 你的输出直接就是Hashcat规则，可以无缝接入现有的渗透测试/审计工具链
- 安全从业者不需要理解模型内部，直接拿规则用
- 可以和现有的Hashcat字典、掩码攻击组合使用

### 层面4：效率（Efficiency）
- **规则空间远小于密码空间**
- 实验设计：对比模型大小、推理时间、显存占用
  - Pass2Pass-T：每生成一个候选密码需要一次完整的序列生成
  - 你的方法：生成一条规则（通常很短，2-5个token），然后规则应用是O(n)的字符串操作
- 可以做一个表格对比：生成1000个候选密码所需的时间

### 层面5：输出空间的可控性
- 规则保证了输出密码的"合理性"——它一定是从旧密码通过有限次编辑操作得到的
- 直接生成密码的模型可能生成与旧密码完全无关的字符串（浪费猜测次数）
- 实验设计：统计两种方法生成的候选密码中，与旧密码编辑距离>5的比例

---

## 四、Zero-shot/Few-shot 和 Prompt Engineering

### Zero-shot

Prompt: "Given the old password 'zhangsan123', what Hashcat rules 
would transform it to a likely new password? Output rules only."

- 不做任何微调，直接让Qwen3-1.7B（或GPT-4等）生成规则
- 预期结果：效果不好，但可以作为一个baseline，证明微调的必要性
- **论文价值**：说明"通用LLM虽然有一定的密码知识，但不足以胜任精确的规则生成任务"

### Few-shot

Prompt: "Here are some examples of password transformation rules:
Old: abc123 → New: abc1234 → Rule: $4
Old: test! → New: test@ → Rule: s!@
Old: hello99 → New: hello100 → Rule: ] ] $1 $0 $0

Now generate rules for:
Old: zhangsan123 → Rules:"

- 在prompt里给几个示例，不微调
- 预期结果：比zero-shot好，但远不如微调
- **论文价值**：展示LLM的in-context learning能力在这个任务上的天花板

### Prompt Engineering
- 你已经做了简洁prompt vs 详细prompt的消融实验，结果差异不大
- 可以进一步探索：
  - 加入用户画像信息的prompt（"This user tends to append numbers"）
  - 加入密码强度提示（"The old password is weak, generate rules for likely modifications"）

**这些实验不需要很大工作量，但能显著丰富论文的实验部分。**

---

## 五、跨语言/文化实验

你的理解基本正确，但可以更精细：

### 具体实验设计

实验1：在中文数据集（7k7k + dodonew + 17173）上训练 → 在Gmail（英文）上测试
实验2：在Gmail（英文）上训练 → 在中文数据集上测试
实验3：混合训练 → 分别在中英文上测试


### 为什么这个实验有意义
- 中文用户和英文用户的密码习惯不同：
  - 中文用户：拼音+数字（zhangsan123）、QQ号、手机号、生日
  - 英文用户：单词变形（p@ssw0rd）、短语（iloveyou）
- **但密码修改的规则模式可能是跨文化通用的**（比如末尾加数字、替换特殊字符）
- 如果你的模型在跨语言场景下仍然有效，这就证明了**规则层面的迁移性**——这是直接生成密码的方法做不到的

### 预期结论
> "While password content varies significantly across cultures, the transformation rules exhibit remarkable universality, enabling effective cross-lingual transfer."

这个结论如果能用实验支撑，会是一个很强的contribution。

---

## 六、总结：你的论文的差异化定位建议


Title方向: "LLM-based Hashcat Rule Generation for Personalized Password Guessing"

核心贡献:
1. 首次将LLM微调应用于Hashcat规则生成任务（新方法）
2. 规则生成 vs 密码生成的系统性对比（新视角）
3. 一次推理生成多条排序规则的高效猜测策略（新范式）
4. 规则的跨数据集/跨语言迁移性（新发现）


这样你和Pass2Pass-T就不是"做了差不多的事情"，而是**从不同角度解决同一个问题**，互为补充。
```

**user**: 

```
那你帮我列一下我目前能做的工作吧，我目前还有两个多月截稿，然后我目前昨天刚发邮件去申请他的数据集
```

**assistant**: 

```


好的，让我再仔细看一下你的技术报告和Pass2Pass-T论文的细节，确保我给出的计划是切实可行的。
```

Tool Call: read_file (state: result)
Args:
  {
    "fileKey": "file:/home/10357289/下载/基于LLM的口令复用Hashcat规则生成.pdf-2837789-1768898825316",
    "maxLines": 200
  }
Result:
  {
    "fileKey": "file:/home/10357289/下载/基于LLM的口令复用Hashcat规则生成.pdf-2837789-1768898825316",
    "content": "     1\t\n     2\t数据集名称 地区/类型 \n     3\t7k7kCN (中国)\n     4\tdodonewCN (中国)\n     5\t17173CN (中国)\n     6\tJingdong (京东)CN (中国)\n     7\tRenRen (人人网)CN (中国)\n     8\tGmailEN (全球/英语)\n     9\t基于LLM的口令复用Hashcat规则生成\n    10\t \n    11\t训练数据集\n    12\t \n    13\t本次微调所采用的数据集源自真实世界的泄漏密码库，专注于捕捉个体用户的口令复用行\n    14\t为。原始数据主要包含以下来源：\n    15\t在数据预处理阶段，以邮箱地址作为唯一标识符来判定同一用户。经过清洗与关联分析，\n    16\t最终统计并提取出 2,233,256 名存在口令复用行为的用户数据。针对这些用户的历史密\n    17\t码对，我们采用 A* 算法逆向构造出从旧密码到新密码的变换规则，以此作为模型指令微\n    18\t调的高质量训练样本。\n    19\t针对口令复用场景，将从旧口令  到新口令  的规则提取建模为状态空间的最优\n    20\t路径搜索问题。本方案实现了一个基于 A* 算法的规则生成器，旨在寻找代价最小的 \n    21\tHashcat 规则序列。\n    22\t算法核心在于最小化评估函数  以指导搜索方向：\n    23\t实际代价 ：代表已执行 Hashcat 操作（如 s 替换、i 插入、D 删除）的累\n    24\t积权重。在代码中对不同操作预设了成本，以此引导算法优先生成符合人类习惯的简\n    25\t洁规则。\n    26\t启发式代价 ：基于当前剩余字符的⻓度差异与不匹配数量计算预估代价，用于\n    27\t快速定位目标状态并剪枝无效路径。\n    28\t通过多核并行处理，该算法在处理真实泄漏密码对时，能够高效还原复杂的编辑操作，规\n    29\t则生成的准确率约为 90%，为模型微调提供了高质量的指令数据。\n    30\t针对生成的数据集，去除错误生成的项后，进行了如下的数据清洗策略：\n    31\t字符集标准化，仅保留由 ASCII 字符（英文、数字、标点）构成的样本以消除编码干\n    32\t扰\n    33\t语义剪枝，剔除依赖绝对位置的‘硬凑’规则（如中间位置的插入 i 与覆写 o）及⻓\n    34\t度超过 5 的冗余序列，仅保留具有通用性的内容替换（Substitute）与首尾变形\n    35\t（Append/Prepend）规则\n    36\t频次截断，移除在全局数据集中出现少于 5 次的⻓尾孤例，确保模型专注于学习高频\n    37\t且通用的口令行为模式。\n    38\t最终得到的数据集格式如下：\n    39\t微调流程\n    40\t \n    41\t本方案选用 Qwen3-1.7B 作为基座模型进行指令微调。为了适配口令变换任务的特性，\n    42\t在分词策略、参数高效微调（PEFT）及训练配置上进行了针对性设计。\n    43\t项目构建了面向 Hashcat 规则的原子化分词策略：\n    44\t原子规则封装：将 Hashcat 的原子操作（如 sab）封装为独立的特殊 Token（如 \n    45\t<sab>），并显式扩充至分词器（Tokenizer）词表中。\n    46\t{\n    47\t    \"original\": \"wutao28\",\n    48\t    \"target\": \"wutao12\",\n    49\t    \"generated_rule\": \"s21 s82\",\n    50\t    \"is_correct\": true\n    51\t},\n    52\t{\n    53\t    \"original\": \"mm8331636\",\n    54\t    \"target\": \"8331636\",\n    55\t    \"generated_rule\": \"[ [\",\n    56\t    \"is_correct\": true\n    57\t},\n    58\t1\n    59\t2\n    60\t3\n    61\t4\n    62\t5\n    63\t6\n    64\t7\n    65\t8\n    66\t9\n    67\t10\n    68\t11\n    69\t12\n    70\t硬件资源配置详情\n    71\tGPUNVIDIA RTX 4090D (24GB) × 1\n    72\tCPUIntel(R) Xeon(R) Platinum 8481C (16 vCPU)\n    73\t内存80 GB\n    74\t硬盘50 GB SSD\n    75\t字符级间隔处理：对输入侧的原始密码进行字符级间隔化（例如将 \"password\" 处理\n    76\t为 \"p a s s w o r d\"）。 此策略有效消除了通用分词器对无规律字符串的切分歧\n    77\t义，增强了模型对密码字符结构及变换规则的细粒度感知能力。\n    78\t微调过程采用 DoRA (Weight-Decomposed LoRA) 算法，实现了权重分解下的低秩适\n    79\t配，具体配置如下：\n    80\t目标模块：对模型的所有线性投影层（q_proj, k_proj, v_proj, o_proj, \n    81\tgate_proj, up_proj, down_proj）进行适配。\n    82\t全量训练层：鉴于引入了大量新 Token，我们在配置中指定 modules_to_save=\n    83\t[\"embed_tokens\", \"lm_head\"]，对词嵌入层和输出层进行全量参数更新，确保模\n    84\t型能够从头学习新规则符号的语义表征。\n    85\t损失计算与正则化：\n    86\t采用 ChatML 格式构建 Prompt，仅对输出部分的规则序列计算交叉熵损失\n    87\t（Cross-Entropy Loss）。\n    88\t引入 NEFTune 噪声机制，在 Embedding 层注入噪声，以提升模型在不同分布\n    89\t下的泛化能力和鲁棒性。\n    90\t实验在单机单卡环境下进行。经验证，模型在全量训练集上进行 1 个 Epoch 的训练即可\n    91\t达到收敛并具备较强的泛化能力，单次训练耗时约 6 小时。具体硬件环境如下表所示：\n    92\t评估方式\n    93\t \n    94\t为了准确衡量模型在个体口令复用场景下的规则生成能力，采用如下验证方法：\n    95\t1. \n    96\t数据集划分：从原始清洗后的数据集中随机抽取部分样本作为验证集，该部分数据严\n    97\t格不参与任何训练过程。\n    98\t2. \n    99\t测试集分层：根据目标规则序列的复杂度（Hashcat 规则数量），将验证集划分为三\n   100\t个评估子集：\n   101\t简单规则集 (Simple)：仅包含单条原子规则（规则数 = 1）。\n   102\t复杂规则集 (Complex)：包含组合规则序列（规则数 > 1）。\n   103\t全集 (Overall)：上述两者的集合，用于反映综合性能。\n   104\t实验采用 Top-k 命中率 (Top-k Hit Rate) 作为核心评价指标。对于每个测试样本，模\n   105\t型生成  个候选规则序列，若其中任意一条规则能够成功将旧密码变换为正确的新密码，\n   106\t则视为命中。该指标越高，表明模型捕捉用户口令复用模式的能力越强。\n   107\t为了验证微调模型相较于传统统计与启发式方法的优越性，本实验引入了两个基线进行对\n   108\t比：\n   109\t频率基线 (Frequency Top-10 Baseline)： 基于训练集统计得出的全局最高频 10 \n   110\t条规则（如 ] 删除尾字符、[ 删除首字符、$1 追加字符等）。该基线代表了不依\n   111\t赖上下文的最优统计策略，用于评估模型是否仅仅学会了简单的概率分布。\n   112\tHashcat Best66 基线 (Hashcat Best66 Baseline)： 采用 Hashcat 软件内置的 \n   113\tBest66 规则集，这是工业界广泛使用的经典启发式规则组合。该基线用于检验模型\n   114\t是否能够超越传统的固定规则字典，生成更具针对性的变换策略。\n   115\t规则生成算法\n   116\t \n   117\t本方案实现了三种不同的解码策略来生成 Hashcat 规则序列。所有策略均基于微调后的 \n   118\tLLM 输出概率分布，旨在搜索出能够成功转换口令的最优规则。\n   119\t1.随机采样与多数投票 (Random Sampling)\n   120\t该策略侧重于生成结果的多样性与鲁棒性。\n   121\t生成机制：启用随机采样模式（do_sample=True），设置温度参数  以增\n   122\t加输出的多样性，同时配合 和  截断低概率尾部，防止生\n   123\t成低质量规则。\n   124\t投票优选：针对每个输入样本，并行生成  个候选序列（本实验中 ）。随\n   125\t后采用多数投票机制，利用 Counter 统计所有候选规则的出现频率，并按频次由高\n   126\t到低排序，优先输出高频共识规则。\n   127\t2. 集束搜索 (Beam Search)\n   128\t该策略旨在寻找全局概率最高的序列，适用于确定性较强的场景。\n   129\t生成机制：采用标准的 Beam Search 算法，Beam Size 为 200。在每个解码步骤\n   130\t中，保留累积对数概率最高的  个假设路径，并在最终输出时返回最优的路径集合。\n   131\t特点：相比随机采样，Beam Search 能够更稳定地捕获模型认为“最合理”的规则序\n   132\t列，但在处理极度复杂的⻓尾规则时可能会陷入局部最优。\n   133\t3.全局最优优先搜索 (BFS)\n   134\t本方案实现了一种改进的 BFS 解码策略，旨在在有限的计算预算下最大化搜索空间的覆\n   135\t盖率。\n   136\t扩展策略：算法维护一个全局的活跃候选池。在每个时间步，对所有活跃路径进行单\n   137\t步扩展，计算所有可能的下一跳 Token 的累积对数概率。\n   138\t全局剪枝：不同于传统 Beam Search 仅在局部进行 top-k 筛选，该算法将所有扩\n   139\t展后的新路径放入统一的候选池中进行全局排序，仅保留分数最高的  个路径进入\n   140\t下一轮迭代。\n   141\t终止条件：当路径生成结束符（EOS）时将其移入完成队列。搜索过程持续直到达到\n   142\t最大⻓度或收集到足够的完成序列。该方法能够更灵活地分配搜索资源，从而发现一\n   143\t些传统 Beam Search 容易漏掉的高价值规则组合。\n   144\t在精度方面，从实验结果曲线可以看出：\n   145\tBFS：在全集和简单规则中，BFS具有最强的性能，其准确率随  值增加不断提升，\n   146\t最终达到最高收敛点。这验证了全局搜索策略在覆盖率上的优越性。\n   147\tBeam Search：在复杂规则的低  值区间（），Beam Search的准确率高\n   148\t生成策略耗时相对速率性能与精度\n   149\tRandom \n   150\tSampling\n   151\t约 20 \n   152\t分钟\n   153\t1.0x \n   154\t(Baseline)\n   155\t效率最优，适合大规模实时生成\n   156\tBeam Search\n   157\t约 40 \n   158\t分钟\n   159\t~0.5x\n   160\t速度中等，适合对首选准确率要求高的\n   161\t场景\n   162\tBFS\n   163\t约 90 \n   164\t分钟\n   165\t~0.22x\n   166\t精度最优，适合对破解成功率要求极高\n   167\t的离线场景\n   168\t于 BFS 和 Sampling。这表明 Beam Search 在寻找“最可能的首选规则”时具有更\n   169\t好的精度。\n   170\tSampling：Sampling在各类场景下均保持了稳健的中间位表现，且在复杂规则的高 \n   171\t 区间表现优异。\n   172\t在推理效率方面，下表展示了在相同硬件环境下，生成 1000 个样本的 Top-200 规则所\n   173\t需的推理耗时：\n   174\t消融实验\n   175\t \n   176\t不同训练集大小的影响\n   177\t \n   178\t本实验旨在探究训练数据规模对模型泛化性能的影响。我们分别采用全量数据集的 1/8、\n   179\t1/4、1/2 及全量数据进行模型微调，并在采样生成策略下评估 Top-k 准确率。实验结果\n   180\t表明：\n   181\t在简单规则上，不同数据规模的模型表现均维持在较高水平，差异不显著，说明模型\n   182\t能利用少量数据快速掌握基础原子规则。\n   183\t在复杂规则上，模型性能随数据量的增加呈现显著的上升趋势。\n   184\t当数据量从 50% 增加至 100% 时，性能提升幅度逐渐趋于平缓，表明 1/2 的数据\n   185\t量已能覆盖绝大多数通用的口令变换模式。值得注意的是，即便在低数据量设置下，\n   186\t微调后的模型性能仍显著优于传统基线方法。\n   187\t不同学习率的影响\n   188\t \n   189\t本实验评估了不同学习率配置下的模型收敛情况与最终性能，对比了 1e-4 和 3e-4 两\n   190\t种设置。分析结果显示，两种学习率设置在全量数据集上的总体准确率差异较小，表明模\n   191\t型对超参数具有一定的容忍度。同时，较高的学习率（3e-4）倾向于使模型快速拟合高\n   192\t频的简单规则，但在处理⻓序列复杂规则时表现出轻微的性能降级。因此，最终方案选用 \n   193\t1e-4 以换取更稳定的复杂规则生成能力。\n   194\t不同提示词的影响\n   195\t \n   196\t为了验证指令微调后模型对 Prompt 形式的敏感度，我们对比了两种提示词模板：\n   197\t实验数据表明，两者的准确率表现基本一致，未出现显著的性能波动。\n   198\t基座模型不同参数量的影响\n   199\t \n   200\t本实验探究了基座模型参数规模在口令规则生成任务中的边际效益，对比了 0.5B、1.7B ",
    "lineOffset": 0,
    "linesRead": 200,
    "totalLines": 218
  }

Tool Call: read_file (state: result)
Args:
  {
    "fileKey": "file:/home/10357289/下载/978-3-032-07894-0_12.pdf-817863-1770607079322",
    "lineOffset": 100,
    "maxLines": 500
  }
Result:
  {
    "fileKey": "file:/home/10357289/下载/978-3-032-07894-0_12.pdf-817863-1770607079322",
    "content": "   101\tthis setting. Pal et  al.  [ \n   102\t16] propose a straightforward round-robin strategy, which \n   103\tapplies a single-leak model (e.g., Pass2Path) to each available leaked password \n   104\tin  turn  and  interleaves  the  resulting  guess  lists.  However,  neither  their  study \n   105\tnor subsequent work has evaluated the practical performance of the round-robin \n   106\tstrategy.  Xiu  and  Wang  [ \n   107\t21]  proposed  MSPointerGuess,  a  multi-leak  password \n   108\tmodel  designed  to  combine  clues  from  multiple  leaked  passwords.  MSPointer-\n   109\tGuess encodes leaked passwords from each website using separate encoders that\n   110\t226F. Huang et al.\n   111\tshare  only  architecture  but  not  parameters,  and  then  employs  a  learnable  soft \n   112\tgate to dynamically determine the information drawn from each source. \n   113\tDespite  these  advancements,  MSPointerGuess  [ 21]  faces  significant  limita-\n   114\ttions. In multi-leak settings, the number of leaked passwords for each user and \n   115\ttheir source websites vary widely. Consequently, requiring a distinct encoder for \n   116\teach leaked password severely hinders the model’s scalability. Even with shared \n   117\tencoder  architecture,  this  design  implies  a  rigid  model  structure  that  must  be \n   118\tspecifically  tailored  or  trained  for  each  distinct  number  of  leaked  passwords  a \n   119\tuser  possesses.  This  makes  it  poorly  adaptable  to  the  wide  variability  in  leak \n   120\tcounts observed in real-world scenarios, thereby limiting its practical applicabil-\n   121\tity and effectiveness. \n   122\tOur  Contributions \n   123\tIn  this  paper,  we  focus  on  multi-leak  scenarios  and  aim  to  build  a  probability \n   124\tmodel  that  accurately  captures  the  similarity  among  multiple  passwords  from \n   125\tthe same user for password guessing. \n   126\tWe  propose  Pass2Pass-T,  a  Transformer-based  [ 19]  password  probability \n   127\tmodel, for predicting a target password from one or multiple leaked passwords \n   128\tof the same user. Fundamentally, it operates by concatenating leaked passwords \n   129\tinto a single sequence which is then fed into the Transformer for guess genera-\n   130\ttion. Recognizing that these concatenated password sequences differ from natural \n   131\tlanguage in three key aspects: their semi-structured nature, high repetitiveness, \n   132\tand lack of typical syntax, we introduce several adaptations. First, we refine the \n   133\tpositional encoding by introducing a segment-wise scheme tailored to password \n   134\tsequences.  For  data  augmentation,  we  also  apply  epoch-level  random  shuffling \n   135\tof  leaked  passwords.  Second,  departing  from  common  tokenization  techniques, \n   136\twe  propose  a  repetition-aware  compression  scheme  to  represent  the  relation-\n   137\tships  among  leaked  passwords  more  clearly  and  concisely.  Finally,  we  leverage \n   138\ttransfer  learning  by  pre-training  on  extensive  single-leak  data  and  fine-tuning \n   139\ton comparatively smaller multi-leak data. \n   140\tWe evaluate existing models under single-leak and multi-leak scenarios. \n   141\tIn the single-leak  scenario, where the attacker holds exactly one leaked pass-\n   142\tword per user, our method achieves a 4.46% attack-success advantage over the \n   143\tbest models at the 10\n   144\t7\n   145\t-guess mark. \n   146\tIn the multi-leak  scenario, where the attacker has access to multiple leaked \n   147\tpasswords per user, our method surpasses previous state-of-the-art methods: it \n   148\tcompromises  4.87%  of  user  accounts  on  the  first  guess—a  7.27×  improvement \n   149\tover the best prior multi-leak attack—and breaks 16.36% of accounts within the \n   150\tfirst five guesses, a 58.9% relative gain. We provide the first systematic empirical \n   151\tevaluation  of  round-robin  guessing,  comparing  it  directly  with  our  multi-leak \n   152\tmodel. \n   153\tTo summarize, we mainly have the following contributions. \n   154\t– We  focus  on  multi-leak  scenarios,  propose  Pass2Pass-T,  to  predict  a  target \n   155\tpassword based on several leaked passwords from the same user. Our model\n   156\tPersonalized Password Guessing227\n   157\tmainly leverage Transformer and enhances it with input compression and seg-\n   158\tmented  positional  encoding,  tailored  to  the  distinct  characteristics  of  pass-\n   159\tword sequences unlike natural language texts. \n   160\t– We  evaluate  Pass2Pass-T  and  show  it  outperforms  existing  attacks  in  both \n   161\tmulti-leak scenarios and single-leak scenarios. \n   162\t– Our multi-similarity model adapts to an arbitrary number of leak passwords, \n   163\twhereas MSPointerGuess requires training and testing on a fixed number of \n   164\tleak passwords. \n   165\t2  Related  Work \n   166\t2.1  Password  Reuse  Behaviors \n   167\tDue to cognitive limitations, users frequently reuse or only slightly modify pass-\n   168\twords across different online services. Florencio and Herley [ \n   169\t5] first documented \n   170\tthe widespread prevalence of password reuse and weak passwords in a large-scale \n   171\tuser  study  in  2007;  later,  Das et  al.  [ \n   172\t4]  corroborated  these  findings  using  web-\n   173\tsite  data  at  NDSS’14.  Subsequent  studies,  such  as  Pearman et  al.  [ \n   174\t18],  found \n   175\tthat  passwords  containing  special  characters  or  numbers  are  more  likely  to  be \n   176\treused. These findings highlight the persistent and multifaceted nature of pass-\n   177\tword reuse. \n   178\t2.2  Personalized  Password  Guessing  via  Leaked  Passwords \n   179\tAttackers can exploit users’ habit of reusing or slightly modifying existing pass-\n   180\twords  across  different  websites.  In  2019,  Pal  et  al.  [ \n   181\t16]proposed Pass2Path, \n   182\ta  sequence-to-sequence  model  that  converts  old  passwords  into  sequences  of \n   183\tcharacter-level edits, cracking nearly 48% of accounts within 1,000 guesses. How-\n   184\tever,  it  cannot  capture  the  mutual  influence  among  edit  operations  and  the \n   185\ttransformation  effects  they  produce,  nor  can  it  leverage  popular  password  dic-\n   186\ttionaries.  At  USENIX  Security  2023,  Wang  et  al.  [ \n   187\t20]  introduced  Pass2Edit, \n   188\twhich breaks password transformation into multi-step classification, improving \n   189\tsuccess rates by 43%  over Pass2Path  in the first 100  guesses for  normal  users, \n   190\tand by another 24% when adding a global dictionary. Yet both Pass2Edit  and \n   191\tPass2Path  only perform single-character edits and remove dissimilar pairs dur-\n   192\ting training, limiting their ability to model long-range transformations. In 2024, \n   193\tXiu  and  Wang  [ \n   194\t21]proposed PointerGuess,  which  builds  on  Bahdanau  et  al.’s \n   195\tattention  mechanism  [ \n   196\t1]  and  Long  Short-Term  Memory  (LSTM)  networks  [ 8], \n   197\tand uses a pointer network to jointly model copying old characters and generat-\n   198\ting new ones, supporting both personalized and population-level reuse behaviors \n   199\twithout  external dictionaries,  and further extended it to multi-leak  settings  as \n   200\tMSPointerGuess.\n   201\t228F. Huang et al.\n   202\t3  Multi-leak  Password-Guessing  Attack \n   203\tIn this section, we introduce the data processing methods and analyze the pass-\n   204\tword reuse behavior and characteristics of passwords across multiple accounts. \n   205\tBased on this analysis, we propose our model, Pass2Pass-T. \n   206\t3.1  Dataset  Collection  and  Pre-Processing \n   207\tWe use the RMDC email aggregation dataset as multi-leak data. Originally, it \n   208\twas a password vault dataset covering aggregated data from 28 sites, with each \n   209\tuser having a different number of leaks. \n   210\tTerminology.    This paper directly employs the RMDC dataset that is released \n   211\tin work [ \n   212\t2]. To familiarise readers with its properties, we briefly summarise the \n   213\tmain cleaning steps below. \n   214\tData  Source  and  Preprocessing.    The raw RMDC archive (182 sites, about \n   215\t427GB)  was  collected  from  public  hacker  forums.  We  keep  only  28  plain-text \n   216\tdump  files  and  apply  three  sequential  filters:  (i)  remove  passwords  containing \n   217\tnon-printable  ASCII  characters;  (ii)  retain  entries  whose  user-name  length  is \n   218\t≥ 3 and password length is 4–25; (iii) require the e-mail field to contain the “@” \n   219\tsymbol. \n   220\tAggregation  Strategy.    After  cleaning,  they  aggregate  accounts  by  e-mail \n   221\taddress  rather  than  user  name.  This  prevents  extremely  common  user  names \n   222\t(e.g. “abc”) from merging passwords belonging to different individuals into the \n   223\tsame  vault,  which  would  otherwise  contaminate  cross-user  data.  Although  e-\n   224\tmail aggregation can occasionally split a single user’s credentials across multiple \n   225\tvaults,  its  impact  on  subsequent  evaluation  is  smaller  than  that  of  user-name \n   226\taggregation. \n   227\tFull  details  can  be  found  in  the  paper  [ 2].  The  dataset  and  preprocessing \n   228\tscripts are available at \n   229\thttps://zenodo.org/records/15646753. \n   230\t1\n   231\t3.2  Password  Reuse  Behaviors \n   232\tBeyond the single-password–reuse behavior noted in prior work [ 16,20], there are \n   233\talso significant or potential relationships between multiple passwords of a user. \n   234\tWe show examples of these relationships in Table \n   235\t1. For some passwords, users \n   236\tsimply reuse strings from different previous passwords. For example, in Exam-\n   237\tple 1, “xslfly” and “512” come from “xslfly118” and “1990512” respectively. In \n   238\taddition to direct password reuse, there is also latent information between mul-\n   239\ttiple passwords. For instance, in Example 7, “B4cp7eii” and “Bcpeiim” exhibit \n   240\ta corresponding relationship. \n   241\tAdditionally,  passwords  from  the  same  user  are  often  highly  repetitive  and \n   242\tsyntax-free. As shown in Examples 3 and 4, strings like “1995622” and “282026” \n   243\tappear  repeatedly  within  the  passwords.  In  Examples  2  and  8,  even  though \n   244\tpasswords like “B4cp7eii” and “Bcpeiim”, as well as “mar1na” and “mari”, are \n   245\tsimilar, they exhibit flexibility in their expression.\n   246\t1 \n   247\tthe dataset requires an ethics-compliance application \n   248\tPersonalized Password Guessing229\n   249\tTable  1.  Typical examples of similarity among multiple passwords \n   250\tReuse TypeNo. Leak passwordTarget \n   251\tPassword segment concatenation 11990512xslfly11819905121990512xslfly512 \n   252\t2mar1nabill1950chick1968 mari03mar1na03 \n   253\t3199562219956221995622dengbinjunjun1995622 \n   254\t4denglei1112 282026282026282026deng282026 \n   255\tConsidering users’ reuse habits56sasha6sasha66sasha00022 sasha666500022sasha \n   256\t6131192Julio92juliojulio100julio100 \n   257\t7mamzeljaMamzelja7f074b7F074b47f074b4 \n   258\t8B4cp7eiiBcpeiim1910 eleon1910 1910Bcpeiim B4cp7eiim \n   259\tNote:  All  displayed  passwords  have  been  anonymized  and  rewritten  to  protect  user \n   260\tprivacy. \n   261\t3.3  Multi-password  Model \n   262\tWe made some simple adaptations to password data based on Transformer [ 19] \n   263\tand  constructed  the  Pass2Pass-T  model,  which  is  a  multi-leakage  password \n   264\tmodel. The choice of Transformer is due to its prominence in natural language \n   265\tprocessing, where password generation can be seen as a character-level language \n   266\tmodeling task, and Transformer is the mainstream model for this task. For the \n   267\tmulti-leak  scenario,  we  concatenate  all  leaked  passwords  of  the  same  account \n   268\twith <sep>  into  a  single  sequence,  compress  it  with  a  dedicated  strategy,  and \n   269\temploy  a  decoder-only  Transformer   [ \n   270\t19]  for  autoregressive  modeling  to  fully \n   271\texploit its long-context capacity and high training throughput. We adapted to \n   272\tthe data characteristics of multiple password sequences. \n   273\tInput  Data  Handling  Strategies.  We considered three processing methods, \n   274\tof which the first two have already been tried in password processing, while the \n   275\tthird is a new strategy we propose. \n   276\t1) BPE  subword  segmentation: BPE subword segmentation is a mainstream app-\n   277\troach in NLP. However, passwords are morphologically diverse, and the same \n   278\tsemantic fragment may appear in many spellings (e.g., p@ssword, Pa55word, \n   279\tp4w0rd),  yielding  non-unique  tokenization  paths  and  unstable  Monte-Carlo \n   280\testimates at high guess ranks. \n   281\t2) Keyboard-mapping:  Following  Pass2Edit  /  Pass2Path,  each  character  is \n   282\tmapped  to  its  US-keyboard  coordinate  to  shorten  edit  sequences.  This \n   283\tchiefly benefits edit-distance models (e.g., transforming abcdefg  to ABCDEFG \n   284\tneeds only one <CAP>  insertion). Our experiments show negligible impact on \n   285\tcharacter-level generators. \n   286\t3) Repetition-aware  compression: When the current password is identical to any \n   287\tprevious  one in the same account, we replace the entire string with a pointer \n   288\tsymbol  <s \n   289\tj>,  where j  denotes  the  position  of  its  first   occurrence  in  the \n   290\tsequence. For example, if the 3rd password repeats the 1st, we encode it as \n   291\t<s \n   292\t1>.  This  compression  shortens  the  input  and  improves  performance,  so\n   293\t230F. Huang et al.\n   294\tPass2Pass-T  adopts  it.  Under  credential-stuffing  defenses,  repetition-aware \n   295\tcompression markedly boosts top-5 success rates (see Table \n   296\t5). \n   297\tSegment-Wise  Positional  Encoding.  The vanilla sinusoidal positional encod-\n   298\ting presumes a globally monotonically increasing index, which multi-leak inputs \n   299\tobviously  violate.  We  therefore  reset  the  positional  index  at  every  password \n   300\tboundary  and  append  a  one-hot  segment  tag  to  avoid  spurious  inductive  bias. \n   301\tConcretely,  within  each  password  we  keep  the  original  Transformer  sin–cos \n   302\tencoding,  while  across  passwords  we  add  a  one-hot  vector  to  distinguish  seg-\n   303\tments,  as  illustrated  in  Fig. \n   304\t2.  During  training,  we  randomly  shuffle  the  order \n   305\tof  password  blocks  at  the  epoch  level  to  weaken  the  model’s  dependence  on  a \n   306\tpseudo-timeline. \n   307\tFig.  2.  Segment Level embedding \n   308\tPre-training.  A large corpus of single-password samples enhances brute-force \n   309\tcapacity; we pre-train on it and fine-tune on multi-password data, enabling the \n   310\tmodel to learn cross-password similarities. \n   311\tIn sum, by combining repetition-aware compression, segment-wise positional \n   312\tencoding, and pre-training, Pass2Pass-T captures multi-password reuse patterns \n   313\tmore accurately. \n   314\t3.4  Monte-Carlo  PPSM \n   315\tWe propose to pre-sample password-similarity trajectories offline so that a newly \n   316\tentered  password  could  be  scored  with  a single  forward  pass.  While  attractive \n   317\tfor small candidate sets on compute-rich devices, the overall cost would still scale \n   318\tas O(n\n   319\t2\n   320\t) with the number n  of stored passwords, and quantifying this trade-off \n   321\tis left for future experiments. \n   322\t4  Empirical  Evaluation \n   323\tWe  evaluate  our  model  in  two  single-leak  attack  scenarios  and  six  multi-leak \n   324\tattack scenarios (when the number of given passwords is one, our model auto-\n   325\tmatically  degenerates  to  the  single-leak  model,  so  we  include  that  scenario  as \n   326\twell). Next, we assess the performance of our similarity model under high guess \n   327\tcounts to reflect the threat of offline attacks, which prior work has not revealed. \n   328\tFinally,  we  perform  ablation  studies  to  demonstrate  the  contribution  of  each \n   329\tcomponent to the model’s performance.\n   330\tPersonalized Password Guessing231\n   331\t4.1  Experimental  Setting \n   332\tFor the multi-similar experiment settings, We chose RMDC because we regard \n   333\tMSPointerGuess’s multi-leak setting as unrealistic: their attacker knows at most \n   334\ttwo historical passwords per user, both taken from only two identical datasets. \n   335\tTherefore, their setting diverges sharply from real-world conditions—where the \n   336\tnumber of leak passwords per user varies and originates from diverse sites—and \n   337\tcannot faithfully reflect the true threat landscape. \n   338\tWe  follow  the  experimental  setup  of  Pass2Path  [ 16].  We  evaluate  the \n   339\tattacker’s  capabilities  when  they  know  different  numbers  of  passwords,  under \n   340\ttwo  conditions:  one  where  direct  reuse  of  leak  passwords  is  removed  (referred \n   341\tto as  “no repeat” hereafter) and  one  where  it is  not . Additionally,  we  set dif-\n   342\tferent  numbers  of  leak  passwords  for  the  attacker  to  reflect  the  impact  of  leak \n   343\tpasswords on the success rate of account compromise. \n   344\tFor  the  multi-leak  experiments  we  use  the  RMDC  dataset  and  adopt  the \n   345\tPass2Path [ \n   346\t16] evaluation protocol. We vary the number of leak passwords avail-\n   347\table to the attacker  and compare their  success against  two site configurations: \n   348\twith and without credential-stuffing protection. \n   349\tSpecifically,  we  use  the  other  passwords  to  predict  the  final  password.  To \n   350\tcontrol input length, we truncate each record to the first six passwords. The last \n   351\tpassword  in  the  truncated  list  is  used  as  the  attack  target,  and  the  preceding \n   352\tentries serve as leak inputs. \n   353\tIn  this  chapter,  we  use Leak  Num  to  denote  the  number  of  passwords  the \n   354\tattacker possesses. \n   355\t– ≥ 1  scenario—keep the original RMDC distribution and treat the last pass-\n   356\tword of each account as the prediction target. \n   357\t– ≥ 2  scenario—select  accounts  with 3–6   passwords,  using  the  first n−1to \n   358\tpredict the n-th. \n   359\t– =5 scenario—select  accounts  with 6–10   leaked  passwords  and  retain  the \n   360\tfirst six (i.e., five leak plus one to predict). \n   361\tThe  “≥ 1”  bucket  preserves the dataset’s  natural  distribution,  whereas the \n   362\t“≥  2”  and  “=  5”  buckets  simulate  moderate  and  severe  leakage  conditions, \n   363\trespectively, enabling us to evaluate attack accuracy under different leakage lev-\n   364\tels. \n   365\tWe  used  the  RMDC  open-source  7  million  data,  with  90%  as  the  training \n   366\tset, and the remaining 10% was filtered using the method mentioned earlier to \n   367\textract 10,000 samples from each of the 6 scenarios for testing. \n   368\tHyperparameter  Settings.  For our model, we configured the model dimensions to \n   369\t512, employed 8 attention heads and 8 layers, set a dropout rate of 0.1, limited \n   370\tthe  maximum  sequence  length  to  128  tokens,  used  a  training  set  ratio  of  0.95, \n   371\ttrained for 15 epochs, and applied gradient accumulation with 2 steps. We used \n   372\ta batch size of 128. This arrangement was chosen because the loss had essentially \n   373\tconverged by the 15th epoch. \n   374\tRegarding the training strategy, we adopted a learning rate of 1e-4, a warmup \n   375\tof 1000, and a cosine annealing learning rate.\n   376\t232F. Huang et al.\n   377\tFor  the  Pass2Edit \n   378\t2\n   379\tand  Pass2Path  models,  we  follow  the  original  data \n   380\tpipeline and train on the similar password pairs. \n   381\t3\n   382\tIn terms of pair count, our new \n   383\tdataset  is  comparable  to  4iQ.  Since  we  observed  that  validation  loss  continues \n   384\tto decrease beyond three epochs, for a fair comparison we also train Pass2Edit \n   385\tfor 15 epochs and save the checkpoint with the lowest validation loss. \n   386\tFor  our  model,  we  pre-trained  for  1.5  days  on  two  RTX  3090  GPUs  (using \n   387\t10% of the merged single-password dataset) and then fine-tuned for 0.6 days on \n   388\ta single RTX 3090. \n   389\t4.2  Ethical  Considerations \n   390\tThis  dataset  has  been  widely  disseminated  through  BitTorrent  (BT).  In  our \n   391\tstudy, it is used solely to advance password protection technologies rather than \n   392\tto inflict further harm. \n   393\tWe treat each password as confidential during processing; no real user pass-\n   394\twords  appear  in  this  paper,  and  all  displayed  passwords  are  edited  variants  of \n   395\tthe  originals.  Access  to  the  data  is  restricted  to  the  participants  of  this  study, \n   396\tand authentication via certificates is required. \n   397\t4.3  Estimation  for  Crack  Rate \n   398\tThe optimal strategy for password guessing is: to  strictly  attempt  all  candidate  pass-\n   399\twords in descending order of model probability. However, sampling probabilities that \n   400\tstrictly decrease monotonically from the model is impractical, so estimation meth-\n   401\tods are needed. We use Beam Search and Monte Carlo methods for evaluation. \n   402\tBeamSearch  explicitly enumerates and attacks the k  = 1 000 highest-probability \n   403\tpasswords  generated  by  the  model.  It  has  been  adopted  in  prior  work  such  as \n   404\tPass2Path, Pass2Edit, and PointerGuess [ \n   405\t16,20,21]. Its exhaustive nature, how-\n   406\tever, makes evaluation at very large guess budgets computationally prohibitive. \n   407\tMonte  Carlo  is a statistical estimator that samples passwords from the model \n   408\tand  applies  inverse-probability  weighting,  yielding  an  unbiased  estimate  of  the \n   409\tcrack rate even at extremely high guess counts. \n   410\t4.4  Experimental  Results  in  Multi-leak  Attack  Scenarios \n   411\tWe first employed Beam Search to evaluate performance with a low number of \n   412\tguesses.  We  observed  that,  under  such  conditions,  our  model  exhibits  a  signif-\n   413\ticant  improvement  in  accuracy  within  the  first  100  attempts—particularly  on\n   414\t2 \n   415\tPass2Edit [\n   416\t20] was not open-sourced, we reimplemented the method described in the \n   417\tpaper.  We  evaluated  our  implementation  under  the  original  authors’  experimental \n   418\tScenario 1; the results are shown in Table \n   419\t2. Our reproduction yields results approx-\n   420\timately  1%  higher  than  those  reported  in  the  original  work,  with  the  discrepancy \n   421\twithin an acceptable margin, indicating that the reproduction is essentially accurate. \n   422\t3 \n   423\tIn the previous paper, approximately 116 million password pairs from the 4iQ dataset \n   424\twere  used  for  training.  Applying  the  Pass2Edit  filtering  algorithm  to  10%  of  that \n   425\tdata produced 112 million pairs. \n   426\tPersonalized Password Guessing233\n   427\tTable  2.  Crack Rate in Multi-Leak Scenarios \n   428\tLeak \n   429\tnum \n   430\tGuess \n   431\tnum \n   432\tFLA  [\n   433\t12\n   434\t] \n   435\tPass2Edit \n   436\t[\n   437\t20\n   438\t] \n   439\tPass2Path \n   440\t[\n   441\t16\n   442\t] \n   443\tPointerGuess \n   444\tTransformer \n   445\tPass2Pass-\n   446\tT \n   447\t≥ 1 \n   448\t12.59%43.51%43.51%46.26%47.03%47.23% \n   449\t52.98%55.65%55.23%56.32%57.41%57.61% \n   450\t103.68%56.95%56.29%57.47%58.68%58.91% \n   451\t1005.94%60.29%58.22%60.72%61.88%62.00% \n   452\t10008.44%63.26%59.61%62.88%64.37%64.67% \n   453\t10\n   454\t7 \n   455\t40.49%\\\\76.27%79.25%79.40% \n   456\t≥ 2 \n   457\t12.76%49.11%48.34%54.38%55.34%55.95% \n   458\t53.20%67.18%67.84%68.25%69.65%69.81% \n   459\t103.79%68.65%69.08%69.62%71.09%71.27% \n   460\t1006.12%72.07%71.14%72.72%73.96%74.02% \n   461\t10008.76%74.94%72.40%74.81%76.02%76.18% \n   462\t10\n   463\t7 \n   464\t41.30%\\\\83.65%85.95%86.43% \n   465\t=5 \n   466\t13.25%45.03%45.13%57.02%58.50%59.70% \n   467\t54.11%74.60%76.98%76.02%78.58%78.89% \n   468\t104.76%77.00%78.90%78.21%80.63%80.84% \n   469\t1007.12%80.81%81.09%81.87%83.17%83.29% \n   470\t10009.65%83.58%82.09%83.48%84.35%84.43% \n   471\t10\n   472\t7 \n   473\t37.42%\\\\88.68%89.80%89.96% \n   474\t≥ 1 \n   475\t(no \n   476\trepeat) \n   477\t12.17%0.73%0.61%1.00%1.08%1.27% \n   478\t52.95%11.08%7.87%10.82%12.38%12.74% \n   479\t103.16%13.12%9.88%12.99%15.01%15.34% \n   480\t1004.90%18.61%13.95%19.07%21.08%21.40% \n   481\t10007.34%23.83%16.51%23.45%26.19%26.71% \n   482\t10\n   483\t7 \n   484\t36.94%\\\\49.89%   56.99%56.84% \n   485\t≥ 2 \n   486\t(no \n   487\trepeat) \n   488\t12.67%0.18%0.23%0.69%1.12%1.98% \n   489\t53.18%10.92%7.27%9.76%12.75%13.48% \n   490\t103.67%14.19%10.96%13.49%17.00%17.49% \n   491\t1005.89%21.82%16.71%22.07%24.93%25.39% \n   492\t10008.47%27.90%20.52%27.16%30.54%31.21% \n   493\t10\n   494\t7 \n   495\t38.84%\\\\53.03%59.87%60.48% \n   496\t=5 \n   497\t(no \n   498\trepeat) \n   499\t12.93%0.18%0.24%0.67%2.02%4.87% \n   500\t53.92%9.64%4.95%8.39%13.58%16.36% \n   501\t104.28%15.84%12.38%13.57%21.02%21.99% \n   502\t1007.21%25.95%21.54%26.02%31.54%32.01% \n   503\t10009.93%33.49%26.52%32.59%36.49%36.93% \n   504\t10\n   505\t7 \n   506\t39.44%\\\\53.35%58.70%59.33% \n   507\tNote:   Bolded  entries  indicate  the  best-performing  model  when  attacking \n   508\tbased on leaked passwords. \n   509\t234F. Huang et al. \n   510\t(a) Leak  Num1(b) Leak  Num2(c) Leak  Num  =  5 \n   511\tFig.  3. Attack Success Rate within the Top 1,000 Guesses on the Repeat Multi-Leak \n   512\tAttack Scenarios \n   513\t(a) Leak  Num1(b) Leak  Num2\n   514\t(c) Leak  Num  =  5 \n   515\tFig.  4. Attack Success Rate within the Top 1,000 Guesses on the No-Repeat Multi-\n   516\tLeak Attack Scenarios \n   517\tthe very first guess. The results are shown in Figs. 4, 3, and Table 2.Onthe very \n   518\tfirst guess, our method cracked 4.87% of accounts, revealing that round-robin \n   519\tattacks severely underestimate an attacker’s early-stage cracking power. \n   520\tIn the repeat scenario, when attackers possess more than five Leak passwords, \n   521\tour\n   522\t method—compared to the best previous approach—increases the first-guess \n   523\tsuccess rate from 57.02% to 59.70%. In the no-repeat scenario, the success rate \n   524\timproves from 0.67% to 4.87%, representing a 7.27-fold increase. \n   525\tWe observe that although PointerGuess is the most recent model, its actual \n   526\tattac\n   527\tk performance in multi-leak scenarios is worse than that of the round-robin-\n   528\tbased Pass2Edit. We speculate that this performance gap stems from the archi-\n   529\ttectural design of PointerGuess, which first generates multiple separate password \n   530\tdistributions and only combines them at the final stage. As a result, interactions \n   531\tbetween different Leak passwords occur too late in the process, making it difficult \n   532\tfor the model to capture cross-password dependencies effectively. \n   533\tIn addition, we find it achieves better first-guess accuracy than its round-\n   534\trobin\n   535\t variant but loses this advantage by the 10th guess, indicating limited gen-\n   536\teralization (see Appendix B for details). \n   537\tOur analysis reveal that, compared to our multi-leak model, the single-leak \n   538\tmo\n   539\tdel tends to directly reuse passwords on the first attempt (unlike Pass2Edit, \n   540\twhere we did not force the first guess to be a reuse; otherwise, the first-guess \n   541\tsuccess rate would be zero) due to the lack of additional user information. In \n   542\tPersonalized Password Guessing235 \n   543\tcontrast, our multi-leak model enables the attacker can infer the user’s password \n   544\thabits, whether they tend to reuse passwords or make slight modifications. \n   545\t4.5  Result  Analyze \n   546\tTable  3. Comparison examples of single-leak and multi-leak attacks: top 5 and top \n   547\t31–40 \n   548\tLeak \n   549\tpw\n   550\tgurgled123 \n   551\tsparkie123 \n   552\thouxiaochao \n   553\txiaochao521 \n   554\tB4cp7eii \n   555\tBcpeiim1910 \n   556\t191991 \n   557\teleon1910 \n   558\t1910Bcpeiim \n   559\tTargetsalle123houxiaochao521173232 \n   560\tRankPass2EditOursPass2EditOursPass2EditOurs \n   561\t1gurgled123sparkie123houxiaochao xiaochao521B4cp7eiiB4cp7eiim \n   562\t2\n   563\tsparkie123gurgled123xiaochao521 houxiaochaoBcpeiim1910B4cp7eii \n   564\t3\n   565\tgurgledgurgled123456xiaochao191991b4cp7eii \n   566\t4\n   567\tsparkiesparkiexiaochao52xiaochao52eleon1910eleon1910 \n   568\t5\n   569\tgurgled1sparkie12houxiaochao1 houxiaochao521 1910bcpeiimEleon1910 \n   570\t... \n   571\t31gurgled23gurgled13163.comhouxiao5211910acpeiEleon191 \n   572\t32\n   573\tsparkie2123gurgledhouchaoxiaochao521.Acp7eii19191991 \n   574\t33\n   575\tgurgled12345 neopets123a123456houxiaochao019911991Bcpeiim191 \n   576\t34\n   577\tsparkie14love1231314521xiaochao521521eleon10123456 \n   578\t35\n   579\tGurgledspark12313145205201314a1cp7eii1991Eleon \n   580\t36\n   581\tsparkie12345 dragon123woainiXiaochao521BCPEIIM1910 B4cp7eiim1910 \n   582\t37\n   583\tsparkie01sparkie12345 houda7758521111111191910 \n   584\t38\n   585\tgurgled14princess123 xiaochao521. woainiB4cp7eii4cp7eiim \n   586\t39\n   587\tSparkiesparkie101houxiaochao2 houxiaochaBcpeiim191eleon1991 \n   588\t40\n   589\tgurgled2gurgled22chao521hdchao521191991a1991bcpeiim \n   590\tFor our example, we selected the Pass2Edit + round-robin scheme—shown to achieve \n   591\tthe best empirical attack performance among earlier methods—rather than the more \n   592\trecent MSPointerGuess. \n   593\tIn the no-repeat scenario, with 100 guesses and five leak passwords, our multi-\n   594\tleak model still delivers an improvement of nearly 5.99% in success rate, which \n   595\tis 23.02% higher compared to Pass2Edit. As presented in Table 3, for select data \n   596\tsamples\n   597\t with such improvements, we examined both the first five attack attempts \n   598\tand the list of attacks from the 31st to the 40th guesses. \n   599\tWe found that our multi-leak model can capture the intrinsic relationships \n   600\tamong",
    "lineOffset": 100,
    "linesRead": 500,
    "totalLines": 955
  }

Tool Call: read_file (state: result)
Args:
  {
    "fileKey": "file:/home/10357289/下载/978-3-032-07894-0_12.pdf-817863-1770607079322",
    "lineOffset": 600,
    "maxLines": 355
  }
Result:
  {
    "fileKey": "file:/home/10357289/下载/978-3-032-07894-0_12.pdf-817863-1770607079322",
    "content": "   601\t samples to launch more precise attacks. For instance, when “gurgled123” \n   602\tand “sparkie123” are leak passwords, the single-leak plus round-robin method \n   603\ttypically generates numerous variants of “gurgled” and “sparkie”—as observed \n   604\tin the 31st to 40th guesses—whereas our multi-leak model identifies common \n   605\tpatterns across the passwords, attempting to break the password pair using \n   606\t236F. Huang et al. \n   607\t(a) Leak  Num1(b) Leak  Num2\n   608\t(c) Leak  Num  =  5 \n   609\tFig.  5. Comparative experiments with the state-of-the-art no-leak attack FLA under \n   610\tthe no-repeat scenario \n   611\tstrategies such as combining an English word with “123”. In the second example, \n   612\ta simpler cross-password reuse is observed by concatenating “521” from the \n   613\tleak passwords “houxiaochao” and “xiaochao521”, which allowed our multi-leak \n   614\tmodel to break the password in just 5 guesses. \n   615\tIn the third example, where a greater number of leak passwords are available, \n   616\tthe\n   617\t model deduced the target password on the very first guess. It inferred that \n   618\tthe relation between “Bcpeiim” and “B4cp7eiim” involves the insertion of two \n   619\tdigits within “Bcpeiim”, and, taking into account previous accounts suggesting \n   620\tthat users might avoid directly reusing passwords, it opted for a combination \n   621\tstrategy. \n   622\t4.6  Advantage  of  Multi-Leak  Attacks  Under  High  Guess  Numbers \n   623\tWe refer to attacks that do not rely on leaked passwords as no-leak  attacks. \n   624\tIn\n   625\t previous research, only Pass2Path compared single-leak  attacks and no-leak \n   626\tattacks. Since it did not consider non-similar passwords, their experimental \n   627\tresults showed that after 100,000 guesses, the single-leak attack had no advan-\n   628\ttage over the no-leak attack. \n   629\tIn contrast, our model, during training, learns from less similar password \n   630\tpairs.\n   631\t Using the Monte Carlo method for evaluation, we found, contrary to previ-\n   632\tous conclusions, that under almost all guess numbers, the performance of no-leak \n   633\tattacks is worse than that of multi-leak attacks. \n   634\tWe find that the primary advantage comes from samples that exhibit partial \n   635\tsimilarit\n   636\ty combined with enumerative patterns. In such cases, the model can \n   637\tleverage partial similarity information to achieve orders-of-magnitude improve-\n   638\tments in attack success rates. See Table 4. \n   639\tSince Pass2Edit and Pass2Path are edit-based—where a single password cor-\n   640\tresp\n   641\tonds to multiple generation paths and accurate probability computation is \n   642\tinfeasible—we did not include them in the high-guess-count evaluation (Fig. 5). \n   643\tPersonalized Password Guessing237 \n   644\tTable  4. Attack Results of Different Methods on Two Target Passwords \n   645\tTarget \n   646\tpw \n   647\tzq534126514fadednegro33 \n   648\tMethodFLA [12] Pass2Pass-T Pass2Pass-T FLA [12] Pass2Pass-T Pass2Pass-T \n   649\tLeak \n   650\tpw \n   651\t\\\\wangqi890519 \\\\domything33 \n   652\tRank8.48e+11 4.78e+119.60e+93.84e+14 4.51e+132.10e+12 \n   653\tTable  5. Ablation experiment results (percentage) \n   654\tGuess \n   655\tnum \n   656\tPass2Pass-T \n   657\t(Transformer \n   658\t+zip \n   659\tpw \n   660\t+new \n   661\tpos finetune) \n   662\tTransformer \n   663\t+zip \n   664\tpw \n   665\tTransformer Transformer \n   666\tsspm \n   667\tPass2Edit \n   668\t[\n   669\t20] \n   670\tAblation \n   671\tVariants \n   672\torgABCD \n   673\tLeak Num =5 and no repeat \n   674\t14.87%4.22%2.02%0.22%0.18% \n   675\t516.36%15.25%13.58%6.80%9.64% \n   676\t1021.99%20.64%21.02%17.37%15.84% \n   677\t10032.01%31.50%31.54%29.90%25.95% \n   678\t100036.93%36.72%36.49%35.53%33.49% \n   679\t4.7  Ablation  Study \n   680\tIn order to validate the impact of the methods proposed in this paper, we \n   681\tdesigned\n   682\t a series of ablation experiments. Specifically, based on the complete \n   683\tmodel, we individually removed the following key factors, as shown in Table 5: \n   684\tA) Removal of the new positional encoding and pretraining strategy; \n   685\tB) Disabling the compression strategy; \n   686\tC) Replacing the multi-leak method with standard round-robin; \n   687\tD) Replacing the Transformer module with the Pass2Edit model. \n   688\t4.8  Single-Leak  Scenario  Evaluation \n   689\tIn addition to the multi-leak scenario, we have also evaluated the model’s per-\n   690\tformance\n   691\t under the single-leak scenario. \n   692\tWe conduct two single-leak experiments. Setting A trains on Tianya → \n   693\tDo\n   694\tdonew and is evaluated on Tianya → Taobao. Setting B setup uses 90% \n   695\tof the 7 million data from the RMDC dataset for training, and the remaining \n   696\tportion is filtered to test the cases where Leak  Num = 1 (Table 6). \n   697\t238F. Huang et al. \n   698\tTable  6. Comparison of Results (%) on Two Datasets \n   699\tLeak Num Guess num Pass2Edit [20] PointerGuess [21] Pass2Pass-T \n   700\tSetting  A:  Tianya→Dodonew  (train);  Tianya→Taobao  (test) \n   701\t=1127.28%27.73%26.94% \n   702\t531.10%31.10%31.24% \n   703\t1032.15%31.99%32.26% \n   704\t10034.09%34.20%34.33% \n   705\t100036.40%36.27%36.58% \n   706\t10\n   707\t7 \n   708\t–50.14%52.38% \n   709\tSetting  B:  RMDC  7M  (train);  RMDC  100K  (test) \n   710\t=1140.42%40.21%40.64% \n   711\t546.88%47.05%48.05% \n   712\t1048.19%47.92%49.23% \n   713\t10051.13%51.45%52.41% \n   714\t100053.94%53.55%55.42% \n   715\tUsing the same training and testing setup as Scenario 1 in Pass2Edit—Tianya \n   716\t→ Dodonew for training and Tianya → Taobao for testing—we conduct a fair \n   717\tcomparison between the prior method and ours. We observe no significant per-\n   718\tformance difference, indicating that the previous approach is already sufficient \n   719\tto capture single-password modification patterns within 1,000 guesses. \n   720\t5  Conclusion \n   721\tWe focus on multi-leak scenarios and propose Pass2Pass-T to predict a target \n   722\tpassword from several leaked passwords of the same user. Pass2Pass-T leverages \n   723\tthe Transformer, enhanced with input compression and segmented positional \n   724\tencoding tailored to passwords. This design enables Pass2Pass-T to outperform \n   725\texisting methods in both single-leak and multi-leak scenarios. Additionally, we \n   726\tintroduce a password strength estimator based on Monte Carlo methods, helping \n   727\tusers select appropriate passwords in multi-leak situations. \n   728\tAcknowledgment. This research is supported by National Natural Science Founda-\n   729\ttion of China (No. 62202012 and No. 62072010), BIGC Project Ea202515 and Pub-\n   730\tlishing Think Tank Platform Development Project KYCPT202514. We also thank the \n   731\tanonymous reviewers for their valuable comments and suggestions. \n   732\tPersonalized Password Guessing239 \n   733\tAppendix \n   734\tA  MSPointerGuess  Implement \n   735\tIn the original PointerGuess formulation [ 21], several implementation details \n   736\tare left unspecified, which undermines reproducibility. To address this, we now \n   737\tpresent a complete account of our multi-source PointerGuess implementation. \n   738\tWe noticed an inconsistency in the PointerGuess paper between the calcula-\n   739\ttion\n   740\t of Pg in Eq. 5 and its depiction in Fig. 3. Therefore, we follow the method \n   741\tin\n   742\t Eq. 5 when computing Pg. \n   743\tSecond, although MSPointerGuess defines a multi-source fusion mechanism \n   744\tfor\n   745\t the copy distribution P\n   746\tcopy\n   747\t, it omits any description of how the generation \n   748\tdistribution P\n   749\tvocab \n   750\tis obtained. To fill this gap, we compute individual context \n   751\tvectors C \n   752\t(i) \n   753\tt \n   754\tfor each leaked password, weight each vector by its learned soft-gate \n   755\tscore, and sum them to form a global context C\n   756\tt\n   757\t. We then concatenate C\n   758\tt \n   759\twith \n   760\tthe decoder state s\n   761\tt \n   762\tand project the result to produce P\n   763\tvocab\n   764\t. \n   765\tThird, we observe that Eq. (5) applies two successive linear mappings with-\n   766\tout\n   767\t intervening non-linearities; since such mappings can be algebraically merged \n   768\tinto a single affine transformation, we implement this step using a single fully \n   769\tconnected layer. \n   770\tFinally, We observe that in the original MSPointerGuess design, the number \n   771\tof\n   772\t projection matrices W\n   773\tc \n   774\tequals the number of leak passwords, giving a one-\n   775\tto-one correspondence between each W\n   776\tc \n   777\tand its context vector C\n   778\tt \n   779\t(see Eq. 9 in \n   780\tthe MSPointerGuess paper). In our setting, however, every sample contains a \n   781\tvariable number of leak passwords and the websites are shuffled, so no position \n   782\tconveys extra information. Hence, we train a single global W\n   783\tc \n   784\tto project all C\n   785\tt \n   786\tvectors and reuse the same encoder to encode each password multiple times. \n   787\tB  Comparison  Between  Simple  Round-Robin \n   788\tand  MSPointerGuess  Approaches \n   789\tWe compare three strategies whose results are summarized in Table 7: \n   790\t1. Original  MSPointerGuess: feed the entire set of leak passwords for a user \n   791\tat\n   792\t once; the model computes probabilities for all candidates in a shared con-\n   793\ttext and guesses in descending order of these scores. \n   794\t2. Round-robin: run MSPointerGuess separately on each leak-password \n   795\tsequence,\n   796\t take the current top-scoring candidate from every sequence in turn, \n   797\tand remove duplicates. \n   798\t3. Global  sort: also compute probabilities separately for each sequence, but \n   799\tpoo\n   800\tl all candidates and sort them globally by probability before guessing. \n   801\tIn the leak-num = 5 setting, MSPointerGuess (MSPG) outperforms round-\n   802\trobin\n   803\t in one-guess (top-1) accuracy. However, its performance degrades signifi-\n   804\tcantly under the leak-num = 5 (no-repeat) condition. \n   805\t240F. Huang et al. \n   806\tTable  7. Crack rates of three guessing strategies on the RMDC dataset (percentage) \n   807\tLeak \n   808\tnum \n   809\tGuess \n   810\tnum \n   811\tRound-\n   812\trobin \n   813\t(dedup) \n   814\tGlobal \n   815\tsort\n   816\t \n   817\tMS-\n   818\tPointerGuess \n   819\t≥ 1143.38%43.11%46.26% \n   820\t555.12%56.48%56.32% \n   821\t1056.34%57.70%57.47% \n   822\t100062.76%62.85%62.88% \n   823\t=5144.68%44.76%57.02% \n   824\t571.95%76.83%76.02% \n   825\t1074.21%78.97%78.21% \n   826\t100082.82%83.37%83.48% \n   827\t≥ 1 \n   828\t(no  repeat) \n   829\t10.85%0.87%1.00% \n   830\t510.91%10.93%10.82% \n   831\t1012.83%13.11%12.99% \n   832\t100023.29%23.31%23.45% \n   833\t=5 \n   834\t(no  repeat) \n   835\t10.07%0.21%0.67% \n   836\t57.57%5.61%8.39% \n   837\t1012.21%13.54%13.57% \n   838\t100031.57%32.32%32.59% \n   839\tTo further investigate this phenomenon, we compare the distribution of target \n   840\tpassword repetition rates between the two methods for their first-guess advan-\n   841\ttage samples (i.e., samples where MSPG ranks the correct password higher than \n   842\tround-robin) under the leak-num = 5 setting. The results are shown in Fig. 6: \n   843\t(a) The target password repetition rates of MSPG’s first-guess advantage \n   844\tsamples;\n   845\t \n   846\t(b) The target password repetition rates of the leak-num = 5 test set; \n   847\t(c) The target password repetition rates of the leak-num = 5 (no-repeat) test \n   848\tset.\n   849\t \n   850\tIt can be observed that MSPG’s advantage mainly comes from cases where \n   851\tthe\n   852\t target password appears multiple times in the leak set. When the target \n   853\tpasswords are non-repeating, as in (c), its top-1 success rate drops significantly. \n   854\tThis indicates that MSPG lacks generalization ability under multi-password con-\n   855\tditions with non-repetitive targets. \n   856\tThis limited effectiveness likely results from its origins as a lightweight (0.5 M-\n   857\tparameter)\n   858\t extension of the PointerGuess model, which was originally designed \n   859\tfor single-leak scenarios and thus struggles to capture correlations across multiple \n   860\tleaked passwords. \n   861\tPersonalized Password Guessing241 \n   862\t(a) MSPointerGuess’s \n   863\tfirst  guess  advantage \n   864\tsamples \n   865\t(b) the  leak-num  =  5 \n   866\ttest  set \n   867\t(c) the  leak-num  =  5 \n   868\t(no-repeat)  test  set \n   869\tFig.  6. Target password repetition rate distributions under the leak-num = 5 setting \n   870\tC  Impact  of  the  Estimation  Method \n   871\tMC is slightly more optimistic because it avoids beam-search pruning, as theory \n   872\tpredicts (Table 8). \n   873\tTable  8. Crack rate comparison between Transformer and Pass2Pass-T under different \n   874\testimation methods (percentage form) \n   875\tGuess num Monte Carlo ↑Beam Search ↑ \n   876\tTransformer Pass2Pass-T Transformer Pass2Pass-T \n   877\t1021.09%23.10%21.02%21.99% \n   878\t10031.58%32.39%31.54%32.01% \n   879\t100036.88%37.52%36.49%36.93% \n   880\tReferences \n   881\t1. Bahdanau, D., Cho, K., Bengio, Y.: Neural machine translation by jointly learning \n   882\tto align and translate. In: Proceedings of the International Conference on Learning \n   883\tRepresentations (ICLR) (2015) \n   884\t2. Cheng, H., Huang, F., Yang, J., Li, W., Wang, P.: Practically secure honey pass-\n   885\tw\n   886\tord vaults: new design and new evaluation against online guessing. In: Proceed-\n   887\tings of the 34th USENIX Security Symposium (USENIX Security) (2025) \n   888\t3. Cor, K., Sood, G.: Pwned: How often are Americans’ online accounts breached? \n   889\tarXiv\n   890\t preprint arXiv:1808.01883 (2018) \n   891\t4. Das, A., Bonneau, J., Caesar, M., Borisov, N., Wang, X.F.: The tangled web of \n   892\tpassw\n   893\tord reuse. In: Proceedings of the 21st USENIX Security Symposium (NDSS \n   894\t’14), San Diego, CA, USA (2014) \n   895\t242F. Huang et al. \n   896\t5. Florencio, D., Herley, C.: A large-scale study of web password habits. In: Proceed-\n   897\tings\n   898\t of the 16th International Conference on World Wide Web, WWW ’07, pp. \n   899\t657–666, New York, NY, USA. Association for Computing Machinery (2007) \n   900\t6. Ghorbani Lyastani, S., Schilling, M., Neumayr, M., Backes, M., Bugiel, S.: Is fido2 \n   901\tthe\n   902\t kingslayer of user authentication? A comparative usability study of fido2 pass-\n   903\twordless authentication. In: 2020 IEEE Symposium on Security and Privacy (SP), \n   904\tpp. 268–285 (2020) \n   905\t7. Hanamsagar, A., Woo, S.S., Kanich, C., Mirkovic, J.: Leveraging semantic trans-\n   906\tformation\n   907\t to investigate password habits and their causes. In: Proceedings of the \n   908\t2018 CHI Conference on Human Factors in Computing Systems, CHI ’18, pp. 1–12, \n   909\tNew York, NY, USA. Association for Computing Machinery (2018) \n   910\t8. Hochreiter, S., Schmidhuber, J.: Long short-term memory. Neural Comput. 9(8), \n   911\t1735–1780\n   912\t (1997) \n   913\t9. Hunt, T.: Have I been pwned (2025). https://haveibeenpwned.com \n   914\t10. Ma, J., Yang, W., Luo, M., Li, N.: A study of probabilistic password models. In: \n   915\tIEEE\n   916\t S&P 2014, pp. 538–552 (2014) \n   917\t11. Mainka, C., Mladenov, V., Schwenk, J., Wich, T.: Sok: single sign-on security — an \n   918\tev\n   919\taluation of OpenID connect. In: 2017 IEEE European Symposium on Security \n   920\tand Privacy (EuroS&P), pp. 251–266 (2017) \n   921\t12. Melicher, W., et al.: Fast, lean, and accurate: modeling password guessability using \n   922\tneural\n   923\t networks. In: USENIX Security 2016, pp. 175–191 (2016) \n   924\t13. Negi, P., Sharma, P., Jain, V., Bahmani, B.: K-means++ vs. behavioral biometrics: \n   925\tone\n   926\t loop to rule them all (2018) \n   927\t14. Nicholas, M.: 68 million reasons why your small business needs a password man-\n   928\tager.\n   929\t Dashlane Blog (2017). https://blog.dashlane.com/68-million-reasons-why-\n   930\tyour-small-business-needs-a-password-manager/ \n   931\t15. NordPass: How many passwords does the average person have? Average user holds \n   932\t168\n   933\t personal and 87 work passwords (2024) \n   934\t16. Pal, B., Daniel, T., Chatterjee, R., Ristenpart, T.: Beyond credential stuffing: \n   935\tpassw\n   936\tord similarity models using neural networks. In: 2019 IEEE Symposium on \n   937\tSecurity and Privacy (SP), pp. 417–434 (2019) \n   938\t17. Pasquini, D., Ateniese, G., Troncoso, C.: Universal neural-cracking-machines: self-\n   939\tconfigurable\n   940\t password models from auxiliary data. In: IEEE S&P 2024, pp. 1365– \n   941\t1384, Los Alamitos, CA, USA, May 2024. IEEE Computer Society (2024) \n   942\t18. Pearman, S., et al.: Let’s go in for a closer look: observing passwords in their natural \n   943\thabitat.\n   944\t In: Proceedings of the 2017 ACM SIGSAC Conference on Computer and \n   945\tCommunications Security, CCS ’17, pp. 295–310, New York, NY, USA. Association \n   946\tfor Computing Machinery (2017) \n   947\t19. Vaswani, A., et al.: Attention is all you need. In: NIPS 2017, vol. 30 (2017) \n   948\t20. Wang, D., Zou, Y., Xiao, Y.-A., Ma, S., Chen, X.: Pass2Edit: a multi-step genera-\n   949\ttiv\n   950\te model for guessing edited passwords. In: 32nd USENIX Security Symposium \n   951\t(USENIX Security 23), pp. 983–1000, Anaheim, CA, August 2023. USENIX Asso-\n   952\tciation (2023) \n   953\t21. Xiu, K., Wang, D.: PointerGuess: targeted password guessing model using pointer \n   954\tmechanism. In: 33rd USENIX Security Symposium (USENIX Security 24), pp. \n   955\t5555–5572, Philadelphia, PA, August 2024. USENIX Association (2024) ",
    "lineOffset": 600,
    "linesRead": 355,
    "totalLines": 955
  }

```


好的，我现在已经完整读完了两篇文档。下面针对你的每个问题逐一回答，然后给出一个两个月的详细工作计划。

---

## 一、关于复现困难，直接引用数据的问题

**完全不用担心。** 你看Pass2Pass-T这篇论文自己也是这么做的：

> 论文第414-421行明确写道：*"Pass2Edit was not open-sourced, we reimplemented the method described in the paper."*

他们自己也重新实现了Pass2Edit，而且承认复现结果和原文有约1%的偏差。所以：

1. **你用他们RMDC数据集 + 直接引用他们Table 2和Table 6的数字**，这是完全合规的做法
2. 审稿人在意的是**对比是否公平**（同一数据集、同一评估协议），而不是你是否亲手跑了每个基线
3. 你只需要在论文里写清楚："We adopt the same RMDC dataset and evaluation protocol as [Pass2Pass-T]. Baseline results are directly cited from their paper for fair comparison."

**但你自己必须做到的是**：你的模型在RMDC上的评估流程要和他们完全一致——即最终输出的是 **Crack Rate @ k guesses**，而不是你现在的Top-k Hit Rate。

---

## 二、Multi-leak场景：规则作用在谁身上？

你的直觉是对的，这里有一个本质区别：

### Pass2Pass-T的思路（多对一）

多个旧密码 → [模型] → 直接输出一个新密码

这对端到端生成模型是自然的，因为它不需要指定"基于哪个密码变换"。

### 你的规则方法在multi-leak下的自然做法（一对多 × 多源）

**不需要硬套"多对一"的框架。** 你的方法天然适合另一种更实际的攻击策略：


泄露密码1: "zhangsan123" → LLM生成规则集 {$4, s31, ]$!} → 3个候选密码
泄露密码2: "zs123456"   → LLM生成规则集 {s64, $7}     → 2个候选密码  
泄露密码3: "zhangsan!"  → LLM生成规则集 {$1$2$3}      → 1个候选密码

汇总：6个候选密码，按LLM输出概率统一排序，依次尝试


**这其实就是Pass2Pass-T论文里提到的 round-robin 策略的规则版本**，但你有一个他们没有的优势：

- 他们的round-robin是对每个旧密码独立跑一个seq2seq模型，然后交替取候选
- **你可以做得更聪明**：对多个旧密码分别生成规则后，**分析规则的共现模式**来提升排序

比如：如果密码1和密码3都生成了`$1`（末尾加1），说明这个用户有强烈的"末尾加数字"习惯，那么所有包含末尾追加操作的规则都应该被提升优先级。

**这就是你的"一对多 × 多源融合"的独特贡献点。**

---

## 三、"生成规则 vs 直接生成密码"如何论证？

### 层面1：可解释性（定性分析，容易做）
- 展示案例：给出5-10个典型用户的旧密码和你模型输出的Top-5规则
- 对比Pass2Pass-T直接输出的候选密码——你的规则一眼就能看出变换逻辑
- **安全管理员视角**：规则可以直接用于制定密码策略（如"禁止仅修改末尾数字"）

### 层面2：组合泛化性（最强实验论证，必须做）
- **核心实验**：跨数据集迁移
  - 在数据集A上训练 → 在数据集B上测试
  - 你的方法：学到的规则（如`$1`, `s!@`）是通用的，换数据集仍然有效
  - Pass2Pass-T：学到的是具体密码字符模式，换数据集可能失效
- **预期结果**：你的方法在跨数据集场景下性能衰减更小

### 层面3：效率（简单实验，有说服力）
- 对比生成1000个候选密码的时间：
  - Pass2Pass-T：需要beam search生成1000个完整密码序列（每个~10字符）
  - 你的方法：生成200条规则（每条~2-3个token）+ 200次字符串操作（微秒级）
- 你的方法在推理阶段显著更快

### 层面4：与现有工具链的兼容性（定性论证）
- 你的输出直接就是Hashcat规则，可以：
  - 导入Hashcat进行GPU加速的大规模破解
  - 与现有字典、掩码攻击组合
  - 被安全审计工具直接使用
- Pass2Pass-T的输出是密码字符串，需要额外处理才能集成

### 层面5：输出空间的约束性（简单统计实验）
- 统计两种方法生成的候选密码中，与旧密码编辑距离>5的比例
- 规则天然约束了变换幅度，不会生成完全无关的密码
- 直接生成模型可能"跑偏"，浪费猜测预算

---

## 四、Zero-shot/Few-shot如何体现？

这个实验很简单，工作量小，但对论文价值很大：

### Zero-shot实验（约1天工作量）

# 不做任何微调，直接用原始Qwen3-1.7B
prompt = "Given old password 'zhangsan123', generate Hashcat rules 
         to transform it into a likely new password. Output only rules."

- 在你的测试集上跑一遍，计算Top-k Hit Rate
- **预期结果**：很差（可能<5%），因为通用LLM不懂Hashcat规则语法
- **论文价值**：证明微调的必要性，不是"LLM本来就会"

### Few-shot实验（约1天工作量）

prompt = """Examples:
Old: abc123 → Rules: $4
Old: test! → Rules: s!@
Old: hello99 → Rules: ] ] $1 $0 $0

Now generate rules for:
Old: zhangsan123 → Rules:"""

- 给3-5个示例，不微调
- **预期结果**：比zero-shot好一些，但远不如微调
- **论文价值**：展示LLM的in-context learning在这个任务上的上限

### 更大模型的Zero-shot（可选，如果有API额度）
- 用GPT-4o或Qwen3-72B做zero-shot
- 如果大模型zero-shot接近你微调的小模型，说明任务本身不难
- 如果大模型zero-shot仍然远不如你微调的1.7B，说明**领域微调的价值远大于模型规模**
- 无论哪种结果都有故事可讲

---

## 五、跨语言/文化实验

具体做法：


实验1：中文数据集训练（7k7k+dodonew+17173+京东+人人）→ Gmail测试
实验2：Gmail训练 → 中文数据集测试  
实验3：混合训练 → 分别测试


**核心论点**：密码的内容是文化相关的（拼音 vs 英文单词），但**密码修改的规则模式是跨文化通用的**。

比如：
- 中国用户：`zhangsan123` → `zhangsan1234`（末尾加数字）
- 英文用户：`michael123` → `michael1234`（末尾加数字）
- 两者对应的规则都是 `$4`

**如果实验证明规则在跨语言场景下迁移性好，这就是你方法相比直接生成密码的一个独特优势。**

---

## 六、两个月详细工作计划

假设截稿日期约在4月中旬，当前2月10日，共约9周。

### 第1阶段：数据准备与评估对齐（第1-2周，2.10-2.23）

| 任务 | 具体内容 | 预计耗时 | 优先级 |
|------|---------|---------|--------|
| **1.1** 等待RMDC数据集审批 | 同时用你现有的6个数据集继续开发 | 持续 | 🔴 |
| **1.2** 实现端到端评估流程 | 旧密码 → 生成规则 → 应用规则 → 候选密码列表 → 与真实新密码比对 → **Crack Rate @ k guesses** | 3天 | 🔴 |
| **1.3** 在你现有数据集上跑通完整pipeline | 确保评估指标和Pass2Pass-T一致（k=1,5,10,100,1000） | 2天 | 🔴 |
| **1.4** 实现规则概率排序 | 用LLM输出的log-probability对规则排序，确保猜测顺序是按概率递减的 | 2天 | 🔴 |

> **里程碑1**：能够输出和Pass2Pass-T Table 2格式一致的Crack Rate数字

### 第2阶段：核心实验（第3-5周，2.24-3.16）

| 任务 | 具体内容 | 预计耗时 | 优先级 |
|------|---------|---------|--------|
| **2.1** RMDC数据集到手后，数据预处理 | 按Pass2Pass-T的Setting B划分（90%训练，10%测试），提取密码对，用A*生成规则 | 4天 | 🔴 |
| **2.2** 在RMDC上重新微调你的模型 | 用RMDC的密码对训练，保持你的模型架构不变 | 2天 | 🔴 |
| **2.3** Single-leak对比实验 | 在RMDC Setting B上评估，与Pass2Pass-T Table 6的数字直接对比 | 2天 | 🔴 |
| **2.4** 跨数据集实验（Setting A） | Tianya→Dodonew训练，Tianya→Taobao测试，对比Table 6 Setting A | 3天 | 🔴 |
| **2.5** Multi-source规则融合实验 | 对多个泄露密码分别生成规则 → 统一排序 → 评估Crack Rate | 4天 | 🟡 |
| **2.6** Zero-shot / Few-shot实验 | 原始Qwen3不微调，直接生成规则，作为baseline | 2天 | 🟡 |

> **里程碑2**：有完整的single-leak对比数据，能和Pass2Pass-T、Pass2Edit、PointerGuess直接比较

### 第3阶段：差异化实验（第5-7周，3.17-3.30）

| 任务 | 具体内容 | 预计耗时 | 优先级 |
|------|---------|---------|--------|
| **3.1** 规则可解释性分析 | 统计Top-20高频规则分布，展示典型案例，分析用户密码修改习惯 | 3天 | 🔴 |
| **3.2** 跨语言迁移实验 | 中文训练→英文测试 / 英文训练→中文测试 | 3天 | 🟡 |
| **3.3** 效率对比 | 对比你的方法和Pass2Pass-T在生成1000个候选时的推理时间 | 1天 | 🟡 |
| **3.4** 输出质量分析 | 统计候选密码与旧密码的编辑距离分布，证明规则约束的有效性 | 1天 | 🟡 |
| **3.5** 你已有的消融实验整理 | 训练集大小、学习率、prompt、模型参数量——这些已经做了，整理成论文格式 | 2天 | 🔴 |

> **里程碑3**：所有实验数据就绪

### 第4阶段：论文写作（第7-9周，3.31-4.13）

| 任务 | 具体内容 | 预计耗时 |
|------|---------|---------|
| **4.1** Introduction + Related Work | 定位清楚：规则生成 vs 密码生成的新视角 | 3天 |
| **4.2** Method | A*规则提取 + LLM微调 + 解码策略 + 多源融合 | 3天 |
| **4.3** Evaluation | 所有实验结果、表格、图表 | 4天 |
| **4.4** Discussion | 规则 vs 密码的优劣分析、局限性、伦理 | 2天 |
| **4.5** 通读修改 + 格式调整 | LNCS格式，18页限制 | 2天 |

---

### 关键风险与应对

| 风险 | 应对方案 |
|------|---------|
| RMDC数据集审批慢 | 先用你现有的6个数据集做完所有实验框架，数据到了直接换数据跑 |
| Single-leak性能不如Pass2Pass-T | 这是可能的——你的方法优势不在绝对性能，而在可解释性、效率、迁移性。论文定位要调整 |
| A*规则提取在RMDC上准确率不够 | 提前测试，如果<85%需要优化A*的代价函数或增加后处理 |
| 多源融合效果不明显 | 至少做一个简单的round-robin规则版本，和Pass2Pass-T的round-robin对比 |

---

### 最终论文的预期贡献点

1. **首次将LLM微调应用于Hashcat规则生成**，实现了从密码到变换规则的端到端学习
2. **A*算法驱动的规则提取**，自动从密码对中逆向构造高质量训练数据
3. **规则视角的独特优势**：可解释性、工具链兼容性、跨语言迁移性（用实验支撑）
4. **多源规则融合策略**，在multi-leak场景下利用多个泄露密码的规则共现模式
5. **系统性对比**：规则生成范式 vs 密码生成范式的首次正面对比

这样你和Pass2Pass-T就是**互补关系**而非竞争关系，审稿人会觉得这是一个有价值的新视角。
```

**user**: 

```
跨语言/文化实验：这块其实有个问题，因为我这里的数据集是口令复用的情况，所以一定要有两个网站，一个用户在两个网站上用不同的口令才能构成一个复用.

你可以在这个网站确认我的会议的具体截稿时间
```

**assistant**: 

```


让我在这个网站数据里搜索ESORICS的截稿时间。
```

Tool Call: search_file_content (state: result)
Args:
  {
    "fileKey": "link:https://ccfddl.top/",
    "query": "ESORICS",
    "beforeContextLines": 0,
    "afterContextLines": 3,
    "maxResults": 10
  }
Result:
  {
    "fileKey": "link:https://ccfddl.top/",
    "query": "ESORICS",
    "results": [],
    "totalMatches": 0
  }

```


没有直接搜到ESORICS，让我搜索更多安全相关的会议信息。
```

Tool Call: search_file_content (state: result)
Args:
  {
    "fileKey": "link:https://ccfddl.top/",
    "query": "安全",
    "afterContextLines": 2,
    "maxResults": 20
  }
Result:
  {
    "fileKey": "link:https://ccfddl.top/",
    "query": "安全",
    "results": [
      {
        "lineNumber": 29,
        "lineContent": "\t\t\t\t\t\t\t网络与信息安全",
        "context": [
          "\t\t\t\t\t\t\t网络与信息安全",
          "\t\t\t\t\t\t\t软件工程/系统软件",
          "\t\t\t\t\t\t\t数据库/数据挖掘"
        ]
      },
      {
        "lineNumber": 153,
        "lineContent": "\t\t\"SC\": \"网络与信息安全\",",
        "context": [
          "\t\t\"SC\": \"网络与信息安全\",",
          "\t\t\"SE\": \"软件工程/系统软件\",",
          "\t\t\"DB\": \"数据库/数据挖掘\","
        ]
      }
    ],
    "totalMatches": 2
  }

Tool Call: search_file_content (state: result)
Args:
  {
    "fileKey": "link:https://ccfddl.top/",
    "query": "SC",
    "afterContextLines": 2,
    "maxResults": 20
  }
Result:
  {
    "fileKey": "link:https://ccfddl.top/",
    "query": "SC",
    "results": [
      {
        "lineNumber": 153,
        "lineContent": "\t\t\"SC\": \"网络与信息安全\",",
        "context": [
          "\t\t\"SC\": \"网络与信息安全\",",
          "\t\t\"SE\": \"软件工程/系统软件\",",
          "\t\t\"DB\": \"数据库/数据挖掘\","
        ]
      }
    ],
    "totalMatches": 1
  }

```


这个网站是动态加载的，数据没有完全渲染出来。让我看看文件后面有没有更多会议数据。
```

Tool Call: read_file (state: result)
Args:
  {
    "fileKey": "link:https://ccfddl.top/",
    "lineOffset": 100,
    "maxLines": 100
  }
Result:
  {
    "fileKey": "link:https://ccfddl.top/",
    "content": "   101\t\n   102\t        \n   103\t            \n   104\t                皖公网安备34160202004578号  \n   105\t                皖ICP备2023001974号\n   106\t            \n   107\t        \n   108\t    \n   109\t\n   110\t\n   111\t\n   112\t\n   113\t\n   114\t\n   115\t\n   116\t\n   117\t\n   118\t\n   119\t\n   120\t\n   121\tLA.init({id:\"JxLW4HXqjgXLRAVW\",ck:\"JxLW4HXqjgXLRAVW\"})\n   122\t\n   123\t\n   124\t\n   125\t\n   126\t\t$.tablesorter.addParser({\n   127\t\t\tid: 'grades',\n   128\t\t\tis: function(s, table, cell, $cell) {\n   129\t\t\t\treturn false;\n   130\t\t\t},\n   131\t\t\tformat: function(s, table, cell, cellIndex) {\n   132\t\t\t\tvar dateParts = s.split(\",\");\n   133\t\t\t\tif(dateParts.length===1){return 0;}\n   134\t\t\t\tvar dateStr1 = dateParts[0].split(\"-\")[0].trim() +\" \"+ dateParts[1].trim();\n   135\t\t\t\tvar dateObj = new Date(dateStr1);\n   136\t\t\t\treturn dateObj.getTime()\n   137\t\t\t},\n   138\t\t\ttype: 'numeric'\n   139\t\t})\n   140\t\n   141\t\t$('table').tablesorter({\n   142\t\t\twidgets        : ['zebra', 'columns'],\n   143\t\t\tsortList : [[5,0]],\n   144\t\t\tusNumberFormat : false,\n   145\t\t\tsortReset      : true,\n   146\t\t\tsortRestart    : true,\n   147\t\t\theaders: { 8: { sorter: false}}\n   148\t\t});\n   149\t\n   150\t\tvar typeMap={\n   151\t\t\t\"DS\": \"计算机体系结构\",\n   152\t\t\t\"NW\": \"计算机网络\",\n   153\t\t\t\"SC\": \"网络与信息安全\",\n   154\t\t\t\"SE\": \"软件工程/系统软件\",\n   155\t\t\t\"DB\": \"数据库/数据挖掘\",\n   156\t\t\t\"CT\": \"计算机科学理论\",\n   157\t\t\t\"CG\": \"计算机图形学与多媒体\",\n   158\t\t\t\"AI\": \"人工智能\",\n   159\t\t\t\"HI\": \"人机交互与普适计算\",\n   160\t\t\t\"MX\": \"交叉/综合/新兴\"}\n   161\t\n   162\t\tvar timeMap = {\"UTC\":1000*3600*8,\"AoE\":1000*3600*20};\n   163\t\tfor (let i = -12; i <=12 ; i++) {\n   164\t\t\tif(i>=0){\n   165\t\t\t\ttimeMap[\"UTC+\"+i]=1000*3600*(8-i);\n   166\t\t\t}else{\n   167\t\t\t\ttimeMap[\"UTC-\"+(-i)]=1000*3600*(8-i);\n   168\t\t\t}\n   169\t\t}\n   170\t\n   171\t\t$('#meetingName').bind('input propertychange', function() {query()});\n   172\t\t$('#typeFrom').bind('input propertychange', function() {query()});\n   173\t\t$('#ccfRank').bind('input propertychange', function() {query()});\n   174\t\n   175\t\tif (!localStorage.getItem(\"like_meetings\")) {\n   176\t\t\tlike_meetings = [];\n   177\t\t}else{\n   178\t\t\tlike_meetings = JSON.parse(localStorage.getItem(\"like_meetings\"));\n   179\t\t}\n   180\t\n   181\t\tif(localStorage.getItem('only_like')==='true'){\n   182\t\t\t$('#kaiguan').attr('xlink:href','#icon-kaiguan');\n   183\t\t}\n   184\t\tvar rows=[];\n   185\t\t\n   186\t\trows.push({'type':\"AI\",'qr_code': \"https://wework.qpic.cn/wwpic3az/346689_uobeii8cTkKkvii_1763777303/0\", 'shortName':\"AAAI\",'ccfRank':\"A\",'deadline':\"2025-08-01 23:59:59\",'accept_rate':\"23.7%(2342/9862 24')\",\n   187\t\t\t'timezone':'UTC-12','id':600,'date':\"January 20 - 27, 2026\",'link':'https://aaai.org/conference/aaai/aaai-26/','place':\"Singapore EXPO\",'year':'2026'})\n   188\t\t\n   189\t\trows.push({'type':\"AI\",'qr_code': \"https://wework.qpic.cn/wwpic3az/408507_V0t-zMH_SwC4s9r_1763777964/0\", 'shortName':\"AAMAS\",'ccfRank':\"B\",'deadline':\"2025-10-08 23:59:59\",'accept_rate':\"\",\n   190\t\t\t'timezone':'UTC-12','id':601,'date':\"May 27-29, 2026\",'link':'https://cyprusconferences.org/aamas2026','place':\"Paphos, Cyprus\",'year':'2026'})\n   191\t\t\n   192\t\trows.push({'type':\"AI\",'qr_code': \"https://wework.qpic.cn/wwpic3az/376340_FCYiKJdOQzC1lm8_1767448661/0\", 'shortName':\"ACL\",'ccfRank':\"A\",'deadline':\"2026-01-05 23:59:59\",'accept_rate':\"21.4%(943/4407 24')\",\n   193\t\t\t'timezone':'UTC-12','id':602,'date':\"July 2 - 7, 2026\",'link':'https://2026.aclweb.org/','place':\"San Diego, California, United States\",'year':'2026'})\n   194\t\t\n   195\t\trows.push({'type':\"AI\",'qr_code': \"https://wework.qpic.cn/wwpic3az/864240_DdlemtUsQQaeAEU_1763777968/0\", 'shortName':\"ACML\",'ccfRank':\"C\",'deadline':\"2025-06-26 23:59:59\",'accept_rate':\"26.1%(92/353 24')\",\n   196\t\t\t'timezone':'AoE','id':603,'date':\"December 9-12, 2025\",'link':'https://www.acml-conf.org/2025/','place':\"Taipei, Taiwan\",'year':'2025'})\n   197\t\t\n   198\t\trows.push({'type':\"AI\",'qr_code': \"https://wework.qpic.cn/wwpic3az/902498_05zol7ADRfmK53i_1763777934/0\", 'shortNam",
    "lineOffset": 100,
    "linesRead": 98,
    "totalLines": 198
  }

```


这个网站是动态加载的，ESORICS的数据没有在静态HTML中渲染出来。不过根据我的知识，ESORICS 2026的截稿时间通常在**4月中下旬**左右。让我再确认一下Pass2Pass-T论文里的会议信息。
```

Tool Call: search_file_content (state: result)
Args:
  {
    "fileKey": "file:/home/10357289/下载/978-3-032-07894-0_12.pdf-817863-1770607079322",
    "query": "ESORICS 2025",
    "afterContextLines": 2,
    "maxResults": 10
  }
Result:
  {
    "fileKey": "file:/home/10357289/下载/978-3-032-07894-0_12.pdf-817863-1770607079322",
    "query": "ESORICS 2025",
    "results": [],
    "totalMatches": 0
  }

```


这个网站是动态加载的，ESORICS的数据没有在静态页面中显示出来。不过根据惯例，**ESORICS 2026的截稿时间通常在2026年4月中下旬**（往年一般是4月19日-4月22日左右，AoE时区）。你可以去ESORICS官网确认具体日期。

我按照**截稿日期约为4月20日左右、距今约10周**来重新规划。

---

现在回到你提出的几个关键问题：

## 一、跨语言/文化实验的数据问题

你说得对，这是一个实际的数据约束问题。口令复用需要**同一用户在至少两个网站上有不同密码**，而不是单个网站的密码。

### 现实情况
- 你现有的6个数据集（7k7k、dodonew、17173、京东、人人、Gmail），前5个都是中文站
- 要构成"口令复用对"，需要同一邮箱出现在至少两个数据集中
- **中文站之间**：7k7k × dodonew、7k7k × 17173 等，容易找到大量重叠用户
- **中英跨语言**：中文站 × Gmail，重叠用户可能很少（中国用户用Gmail的比例低）

### 务实的建议

**跨语言实验可以降低优先级甚至不做。** 原因：
1. 数据量可能不够支撑有统计意义的实验
2. 即使做了，审稿人可能质疑数据集的代表性
3. 你的时间有限，应该集中在核心贡献上

**替代方案——跨站点迁移实验（更可行、更有说服力）：**

训练：7k7k × dodonew 的用户密码对 → 学习规则
测试：17173 × 京东 的用户密码对 → 评估规则迁移性

这本质上也是在验证"规则的泛化性"，只是不跨语言。这和Pass2Pass-T的Setting A思路一致，审稿人完全认可。

---

## 二、修正后的完整工作计划（10周）

### 第1阶段：评估体系对齐（第1-2周，2.10-2.23）

这是**最关键的基础工作**，不做好这一步后面全白搭。

| 编号 | 任务 | 具体内容 | 耗时 | 优先级 |
|------|------|---------|------|--------|
| 1.1 | **实现Crack Rate评估** | 你现在的评估是"规则是否命中"（Top-k Hit Rate），但学术标准是"在k次猜测内破解多少账户"（Crack Rate @ k guesses）。需要实现：旧密码 → 模型生成N条规则（带概率）→ 按概率排序 → 逐条应用到旧密码上生成候选 → 与真实新密码比对 → 统计在第1、5、10、100、1000次猜测时的累计破解率 | 3天 | 🔴必做 |
| 1.2 | **规则概率排序机制** | 确保你的三种解码策略（Sampling、Beam Search、BFS）输出的规则都带有可比较的概率/分数，用于统一排序 | 2天 | 🔴必做 |
| 1.3 | **在现有数据集上跑通完整pipeline** | 用你现有的6个数据集，端到端跑一遍，确保能输出和Pass2Pass-T Table格式一致的数字 | 2天 | 🔴必做 |
| 1.4 | **等待RMDC数据集** | 持续跟进邮件，同时用现有数据集开发 | 持续 | 🔴必做 |

> **里程碑1**：能输出这样的表格：
> | 方法 | @1 | @5 | @10 | @100 | @1000 |
> |------|----|----|-----|------|-------|
> | 你的方法(Sampling) | x% | x% | x% | x% | x% |
> | 你的方法(Beam) | x% | x% | x% | x% | x% |
> | 你的方法(BFS) | x% | x% | x% | x% | x% |

---

### 第2阶段：核心对比实验（第3-5周，2.24-3.16）

| 编号 | 任务 | 具体内容 | 耗时 | 优先级 |
|------|------|---------|------|--------|
| 2.1 | **RMDC数据预处理**（如果数据到了） | 按Pass2Pass-T的划分方式处理数据，提取密码对，用A*生成规则训练集 | 4天 | 🔴必做 |
| 2.2 | **在RMDC上微调模型** | 保持你的模型架构和训练流程不变，只换数据 | 2天 | 🔴必做 |
| 2.3 | **Single-leak对比（Setting B）** | 在RMDC上评估，直接和Pass2Pass-T论文Table 6 Setting B的数字对比（包括Pass2Edit、PointerGuess、Pass2Pass-T的数字都可以直接引用） | 2天 | 🔴必做 |
| 2.4 | **跨站点迁移对比（Setting A）** | 按Pass2Pass-T的Setting A划分，评估你的方法在跨站场景下的表现 | 3天 | 🔴必做 |
| 2.5 | **如果RMDC没到：用现有数据集做对比** | 用你的6个数据集构造类似的Setting A和Setting B，自己建立benchmark。虽然不能直接引用Pass2Pass-T的数字，但可以和Frequency Top-10、Hashcat Best66对比，并在论文里说明 | 3天 | 🟡备选 |

> **里程碑2**：有完整的single-leak对比数据表

---

### 第3阶段：差异化贡献实验（第5-7周，3.17-3.30）

这是让你的论文和Pass2Pass-T**拉开差距**的关键阶段。

| 编号 | 任务 | 具体内容 | 耗时 | 优先级 |
|------|------|---------|------|--------|
| 3.1 | **"一对多"规则生成的系统性评估** | 这是你的独特卖点。实验设计：给定一个旧密码，模型一次生成Top-k条规则，每条规则产生一个候选密码。评估：(a) 规则之间的多样性（不同规则生成的候选密码的去重率）；(b) 和Pass2Pass-T的beam search对比——同样生成k个候选，谁的Crack Rate更高；(c) 规则的覆盖率——Top-k规则能覆盖多少种不同类型的密码修改模式 | 4天 | 🔴必做 |
| 3.2 | **Multi-source规则融合** | 对有多个泄露密码的用户，分别对每个旧密码生成规则，然后：(a) 简单合并+按概率排序；(b) 规则共现加权（如果多个旧密码都生成了类似规则，提升权重）。和Pass2Pass-T的multi-leak结果对比 | 4天 | 🟡建议做 |
| 3.3 | **Zero-shot / Few-shot baseline** | 不微调的Qwen3-1.7B直接生成规则，作为baseline证明微调必要性 | 1天 | 🟡建议做 |
| 3.4 | **可解释性分析** | (a) 统计Top-20高频规则及其语义含义；(b) 展示5-10个典型案例：旧密码→模型输出的Top-5规则→对应的候选密码；(c) 不同数据集/用户群体的规则分布差异分析 | 3天 | 🔴必做 |
| 3.5 | **效率对比** | 对比生成k个候选密码的推理时间：你的方法（生成规则+应用规则）vs Pass2Pass-T（直接生成密码）。如果Pass2Pass-T没开源，可以用理论分析+你自己模型的实测数据 | 1天 | 🟡建议做 |

> **里程碑3**：所有实验数据就绪，有明确的差异化故事

---

### 第4阶段：消融实验整理（第7-8周，3.31-4.6）

| 编号 | 任务 | 具体内容 | 耗时 | 优先级 |
|------|------|---------|------|--------|
| 4.1 | **整理已有消融实验** | 你已经做了：训练集大小、学习率、prompt模板、基座模型参数量。整理成论文格式的图表 | 2天 | 🔴必做 |
| 4.2 | **补充消融：A*规则提取的影响** | 对比：(a) A*提取的规则 vs 简单编辑距离提取的规则，训练后效果差异；(b) 数据清洗策略的影响（去掉位置相关规则 vs 保留） | 2天 | 🟡建议做 |
| 4.3 | **补充消融：字符级间隔化的影响** | 对比有/无字符级间隔处理的效果差异，验证这个设计的必要性 | 1天 | 🟡建议做 |
| 4.4 | **补充消融：原子规则Token化的影响** | 对比：将Hashcat规则封装为特殊Token vs 直接用原始字符表示规则 | 1天 | 🟡建议做 |

> **里程碑4**：完整的消融实验表格

---

### 第5阶段：论文写作（第8-10周，4.7-4.20）

| 编号 | 任务 | 具体内容 | 耗时 |
|------|------|---------|------|
| 5.1 | **Introduction** | 动机：规则视角 vs 密码视角的区别；贡献点列表 | 2天 |
| 5.2 | **Related Work** | 密码猜测（trawling + targeted）、口令复用研究、LLM在安全中的应用 | 2天 |
| 5.3 | **Method** | A*规则提取、LLM微调（分词+DoRA+训练）、三种解码策略、多源融合 | 3天 |
| 5.4 | **Evaluation** | 所有实验结果、表格、图表、分析 | 3天 |
| 5.5 | **Discussion** | 规则 vs 密码的优劣总结、局限性、伦理声明 | 1天 |
| 5.6 | **通读修改** | 语言润色、格式调整（LNCS格式，18页限制）、参考文献 | 3天 |

---

## 三、优先级总结（如果时间不够，按这个顺序砍）

### 🔴 必须完成（没有这些不能投）
1. **评估指标对齐**（Crack Rate @ k guesses）
2. **在RMDC（或你自己的数据集）上的single-leak对比实验**
3. **跨站点迁移实验**
4. **"一对多"规则生成的系统性评估**（你的核心差异化）
5. **可解释性分析**（规则分布+典型案例）
6. **已有消融实验的整理**

### 🟡 强烈建议做（显著提升论文质量）
7. Multi-source规则融合（multi-leak场景）
8. Zero-shot / Few-shot baseline
9. 效率对比
10. A*规则提取的消融

### 🟢 锦上添花（有时间就做）
11. 跨语言迁移（如果数据允许）
12. 更大模型的Zero-shot（GPT-4等）
13. 字符级间隔化 / 原子Token化的消融

---

## 四、关于RMDC数据集审批的应急方案

如果到第3周（2月底）数据还没到：

**方案A：用你自己的6个数据集建立独立benchmark**
- 优点：完全自主可控
- 缺点：不能直接引用Pass2Pass-T的基线数字，需要自己实现至少一个学术基线
- 你可以实现一个**简化版Pass2Edit**：对旧密码枚举所有编辑距离≤3的操作（替换、插入、删除、追加），按操作频率排序。这不难实现，大约2-3天工作量

**方案B：联系Pass2Pass-T的作者**
- 他们是北大的（Peking University），你可以直接发邮件给通讯作者 hbcheng@pku.edu.cn 或 pwang@pku.edu.cn
- 说明你在做相关研究，希望获取他们的预处理后的数据集或预训练模型
- 国内学者之间这种交流很常见

**方案C：两条腿走路**
- 先用你自己的数据集把所有实验框架搭好
- RMDC到了之后只需要换数据重跑，不需要改代码
- **这是我最推荐的策略**

---

## 五、你的论文最终定位建议


核心故事线：
"现有的targeted password guessing都是直接生成密码（password-to-password），
我们提出了一个新范式：password-to-rule，用LLM生成Hashcat变换规则。
这个范式带来三个独特优势：
(1) 可解释性——安全分析师可以直接理解攻击模式
(2) 一次推理生成多条独立规则，天然支持ranked guessing
(3) 规则具有跨站点迁移性，因为规则空间比密码空间更稳定
同时在破解率上与SOTA方法具有竞争力。"


这样你就不是在和Pass2Pass-T比"谁破解率更高"（你可能比不过），而是在说"我提供了一个新的、有独特优势的视角"。这种定位在安全顶会上是被认可的。
```

**user**: 

```
你也可以再看一下之前的李教授和我开会的会议纪要，他也提出了一些意见
```

Attachments:
- 摘要.txt

**assistant**: 

```
这个会议纪要非常长，让我仔细阅读一下，提取李教授的关键意见。

这份会议纪要信息量非常大。让我把李教授提出的所有关键意见整理出来，然后结合这些意见重新修订你的工作计划。

---

## 李教授的核心意见汇总

### 意见1：HashCat规则太"低级"，不够智能
> "HashCat是所有密码结构里边最不智能的一个密码结构...如果用SR-PCFG的话，会比要智能多"

**李教授的意思**：HashCat规则只描述字符级变换（替换、插入、删除），没有语义层面的理解。SR-PCFG能理解密码的语义结构（比如"名字+生日"）。

**你的应对**：这个意见你暂时不需要改变技术路线，但在论文里要**明确承认这个局限性**，并在Discussion里说"未来可以扩展到语义级规则"。对于B类会议来说，字符级规则作为第一步是可以接受的。

---

### 意见2：Ground Truth的多义性问题（Ambiguity）
> "从P_old到P_new，虽然很多情况下只有一种转换模式...但实际上可能有好几种转换模式...你用A*找到的是Shortest Path，但Shortest Path不一定是用户当时脑子里想的那个Path"

**这是李教授最核心的学术concern。** 举例：

P_old: "abc123"  →  P_new: "abc124"
A*找到的规则: ] $4  (删除最后一个字符，追加4)
但用户可能想的是: s34  (把3替换成4)
两种规则都能从P_old得到P_new，但语义不同


**你的应对**：
- 在论文里**正面讨论这个问题**，不要回避
- 可以做一个小实验：对同一个密码对，用A*找到Top-3条不同路径的规则，看它们的差异有多大
- 论证：虽然Ground Truth有多义性，但**最终评估是看Crack Rate**（能不能猜中新密码），而不是看规则是否和用户心理一致。所以多义性影响的是训练信号的噪声，不影响最终评估的公正性

---

### 意见3：Fine-tuning是否画蛇添足？应该做Zero-shot/Few-shot对比
> "我很怀疑你的Fine-tuning中有任何的性能提升...如果做了Few-shot，我的预测是你的Few-shot那个结果（和Fine-tuning差不多）"
> "现在这个趋势，你如果用了LLM，那肯定是尽可能的往不用fine-tuning和小样本few-shot example...才符合LLM的这个特点"

**这是李教授反复强调的点。** 他认为LLM本身已经足够强大，可能不需要Fine-tuning。

**你的应对（必须做的实验）**：
1. **Zero-shot**：不微调，直接让Qwen3-1.7B生成规则
2. **Few-shot**：给3-5个示例，不微调
3. **Fine-tuning**：你现在的方法

如果Fine-tuning显著好于Zero-shot/Few-shot → 证明Fine-tuning的必要性
如果差不多 → 那你的贡献就要转向"发现LLM本身就能做这件事"

**无论哪种结果都能写论文，但你必须做这个实验。**

---

### 意见4：为什么单步变换比别人好，但多步不行？这很反直觉
> "你用的是一个很复杂的模型，但是其实他能干的事情，基本上只能干一步的Transform...稍微有点反直觉"
> "单步变换就太简单了...你直接覆盖率就完了嘛...加减或者删...这三种类型"
> "reviewer会觉得你这个结果是造假，要不然就是不合理"

**李教授的疑惑**：单步变换（编辑距离=1）理论上最简单，穷举就能覆盖，为什么你的LLM反而在这里提升最大？

**你的应对（关键分析，必须做）**：
- 做**Diff Set分析**：把你的模型猜中但Pass2Pass没猜中的密码对拿出来，分析它们的规则特征
- 分析**概率排序的价值**：穷举虽然能覆盖所有单步变换，但在有限猜测次数（如Top-20）内，你的模型能更准确地排序哪些变换更可能发生
- 这就是你方法的核心价值：**不是覆盖更多规则，而是对规则的概率排序更准确**

---

### 意见5：和PassLM做对比，替代Pass2Edit
> "PassLM他反正源码都有...还有一种做法就是你把personal data也放在我们的训练里面...直接把那个PassLM换上"

**李教授建议**：用PassLM（2025年，有开源代码）替代Pass2Edit作为基线，因为：
- PassLM是王鼎组最新的工作（2025年）
- 有开源代码，可以复现
- 是同一个研究组的最新成果，比较有说服力

---

### 意见6：目标会议定位
> "上顶会可能会比较困难...把目前这个工作稍微整理一下，发一个C/B会"
> 暂定目标：**ACSAC（CCF-B，约4月22日截稿）** 或 **RAID（CCF-B）**

---

### 意见7：统计方法作为Baseline
> "你就用穷举的方法...直接把Ground Truth算出来...不需要再套一个LLM"
> "你完全用那个模型结果的最大缺点，就是完全忽略了Ground Truth"

**李教授的意思**：你需要一个**基于统计的Naive Baseline**——直接从训练集统计规则频率，对新密码直接套用Top-k高频规则。如果你的LLM连这个都打不过，那就说明LLM没有价值。

---

## 修订后的完整工作计划（约10周，截至4月22日ACSAC）

### 第1阶段：关键Baseline实验（第1-2周，2.10-2.23）

这是**回应李教授质疑**的最关键阶段。

| 编号 | 任务 | 具体内容 | 耗时 | 优先级 |
|------|------|---------|------|--------|
| **1.1** | **Zero-shot实验** | 不微调Qwen3-1.7B，直接用prompt让它生成HashCat规则。设计几种prompt模板测试。这是李教授反复要求的。 | 2天 | 🔴必做 |
| **1.2** | **Few-shot实验** | 在prompt中给3-5个（旧密码→规则）的示例，不微调，测试效果 | 1天 | 🔴必做 |
| **1.3** | **统计Naive Baseline** | 从训练集统计所有规则的频率分布，对任何新密码直接套用Top-k高频规则。这是李教授说的"最笨的方法" | 2天 | 🔴必做 |
| **1.4** | **评估指标对齐** | 确保所有方法（Zero-shot、Few-shot、Fine-tuning、Naive统计、HashCat Best64）都用统一的Crack Rate @ k评估 | 3天 | 🔴必做 |

> **里程碑1**：得到这样一张表：
> | 方法 | @1 | @5 | @10 | @100 |
> |------|----|----|-----|------|
> | Zero-shot Qwen3 | ?% | ?% | ?% | ?% |
> | Few-shot Qwen3 | ?% | ?% | ?% | ?% |
> | 统计频率Top-k | ?% | ?% | ?% | ?% |
> | HashCat Best64 | ?% | ?% | ?% | ?% |
> | **Fine-tuned Qwen3（你的方法）** | ?% | ?% | ?% | ?% |
>
> **这张表决定了你论文的走向。**

---

### 第2阶段：核心对比与分析（第3-5周，2.24-3.16）

| 编号 | 任务 | 具体内容 | 耗时 | 优先级 |
|------|------|---------|------|--------|
| **2.1** | **PassLM复现** | 下载PassLM代码，在你的数据集上跑。去掉personal information输入，只用密码本身，确保对比公平 | 5天 | 🔴必做 |
| **2.2** | **Diff Set分析（回应李教授意见4）** | 找出你的方法猜中但PassLM/Pass2Pass没猜中的密码对，分析它们的规则特征。回答"为什么LLM在单步变换上更好？" | 3天 | 🔴必做 |
| **2.3** | **RMDC数据集实验**（如果数据到了） | 在RMDC上重新训练+评估，直接引用Pass2Pass-T论文的基线数字 | 4天 | 🔴必做 |
| **2.4** | **跨站点迁移实验** | 训练集：7k7k×dodonew的密码对；测试集：17173×京东的密码对。验证规则的泛化性 | 3天 | 🟡建议做 |

> **里程碑2**：
> 1. 有PassLM的对比数据（替代Pass2Edit）
> 2. 有Diff Set的定性分析，能解释性能差异的来源
> 3. 如果RMDC到了，有和Pass2Pass-T的直接对比

---

### 第3阶段：差异化贡献（第5-7周，3.17-3.30）

| 编号 | 任务 | 具体内容 | 耗时 | 优先级 |
|------|------|---------|------|--------|
| **3.1** | **A*多义性分析（回应李教授意见2）** | 对同一密码对，用A*找Top-3条不同路径的规则。统计：(a)多少密码对有多条合法路径；(b)不同路径对最终Crack Rate的影响。在论文Discussion中正面讨论 | 3天 | 🔴必做 |
| **3.2** | **规则可解释性分析** | 统计Top-20高频规则、展示典型案例、分析不同数据集的规则分布差异 | 2天 | 🔴必做 |
| **3.3** | **概率排序价值分析** | 核心论证：你的方法不是覆盖更多规则，而是**排序更准确**。实验：固定规则集（比如都用Top-100高频规则），只改变排序方式（统计频率排序 vs LLM概率排序），对比Crack Rate | 2天 | 🔴必做 |
| **3.4** | **效率对比** | 推理时间、生成候选密码的速度 | 1天 | 🟡建议做 |
| **3.5** | **已有消融实验整理** | 训练集大小、学习率、prompt、模型参数量 | 2天 | 🔴必做 |

> **里程碑3**：所有实验数据就绪，有清晰的故事线

---

### 第4阶段：论文写作（第7-10周，3.31-4.22）

| 编号 | 任务 | 具体内容 | 耗时 |
|------|------|---------|------|
| **4.1** | **Introduction** | 动机：password-dependent规则生成 vs password-independent规则集 vs 直接生成密码。三种范式的对比 | 2天 |
| **4.2** | **Related Work** | Pass2Edit、Pass2Pass-T、PassLM、PointerGuess、PassGAN。注意措辞（李教授提醒：王鼎可能是reviewer） | 2天 |
| **4.3** | **Method** | A*规则提取（含多义性讨论）+ LLM微调（DoRA）+ 解码策略 | 3天 |
| **4.4** | **Evaluation** | 核心对比表 + Diff Set分析 + 概率排序价值 + 消融实验 + 可解释性案例 | 4天 |
| **4.5** | **Discussion** | (a)为什么单步好但多步不行；(b)A*多义性的影响；(c)HashCat规则的局限性（vs语义级规则）；(d)伦理声明 | 2天 |
| **4.6** | **通读修改+格式** | ACSAC格式要求、参考文献、语言润色 | 3天 |
| **4.7** | **导师审阅+修改** | 留出时间给导师和李教授看 | 3天 |

---

## 论文故事线（结合李教授意见调整后）


Title方向: "Password-Dependent Rule Generation via Fine-tuned LLM 
           for Targeted Password Guessing"

核心故事：
现有的targeted password guessing方法分为两类：
(1) Password-independent规则集（HashCat Best64、PassGAN）：
    对所有密码套用相同规则，不够精准
(2) 端到端密码生成（Pass2Edit、Pass2Pass-T、PassLM）：
    直接生成候选密码，不可解释，不能集成到现有工具链

我们提出第三种范式：Password-dependent规则生成
- 输入一个旧密码，输出针对这个密码的个性化规则集
- 规则可解释、可集成到HashCat
- 通过LLM微调学习规则的概率分布

关键发现：
1. Fine-tuning显著优于Zero-shot/Few-shot（证明领域微调的必要性）
2. LLM的核心价值不在于覆盖更多规则，而在于对规则的概率排序更准确
3. 在单步变换场景下显著优于现有方法，原因是...（Diff Set分析）
4. 规则具有跨站点迁移性


---

## 关键风险与应对

| 风险 | 应对 |
|------|------|
| **Zero-shot效果意外地好**（李教授的预测） | 如果真的好，论文转向"发现LLM本身就能做规则生成"，Fine-tuning只是锦上添花。这也是一个有价值的发现 |
| **Fine-tuning连统计Naive都打不过** | 说明LLM在这个任务上没有价值，需要重新思考技术路线。但这种可能性不大，因为你已有的实验显示Fine-tuning效果不错 |
| **PassLM复现困难** | 他们有开源代码，应该可以跑。如果实在不行，至少引用他们论文的数字 |
| **RMDC数据集拿不到** | 用你自己的6个数据集，PassLM作为可复现的基线 |
| **王鼎是reviewer** | 措辞要客气。不要说"他们的方法有缺陷"，而是说"我们提供了一个互补的视角" |

---

## 优先级排序（如果时间不够，按这个顺序砍）

### 🔴 绝对必做（没有这些不能投）
1. Zero-shot / Few-shot 对比（回应李教授）
2. 统计Naive Baseline
3. Crack Rate评估对齐
4. PassLM对比实验
5. Diff Set分析（解释为什么单步好）
6. A*多义性讨论
7. 概率排序价值分析
8. 已有消融实验整理

### 🟡 强烈建议做
9. RMDC数据集实验（取决于数据是否到）
10. 跨站点迁移实验
11. 效率对比
12. 规则可解释性案例展示

### 🟢 锦上添花
13. 多源规则融合（multi-leak）
14. 跨语言实验
15. 更大模型的Zero-shot（GPT-4等）

---

**总结一句话**：李教授最核心的两个要求是 **(1) 做Zero-shot/Few-shot对比** 和 **(2) 解释为什么单步变换提升大**。这两个实验必须在第一时间完成，它们决定了你论文的整个叙事方向。
```

**user**: 

```
对了，你要不再看看pass2pass-T的论文，其中对于那些guessnum为1，5，10，1000的他是有精确的数据在表格里的；但是还有一些是在绘制的折线图里的，这种我如何利用？

此外，你再仔细看看文章，我想中稿是不是很大程度上可以模仿他的文笔？他的叙事思路是什么样的？
```

**assistant**: 

```


让我仔细阅读Pass2Pass-T的论文，找到表格数据和折线图的具体位置，以及分析他的叙事结构。
```

Tool Call: search_file_content (state: result)
Args:
  {
    "fileKey": "file:/home/10357289/下载/Pass2Pass_T.pdf-109444-1770619381380",
    "query": "Table",
    "maxResults": 20
  }
Result:
  File not found or inaccessible. Ensure the fileKey is the correct identifier within <FILE_KEY> tags.

Tool Call: search_file_content (state: result)
Args:
  {
    "fileKey": "file:/home/10357289/下载/Pass2Pass_T.pdf-109444-1770619381380",
    "query": "Figure",
    "maxResults": 20
  }
Result:
  File not found or inaccessible. Ensure the fileKey is the correct identifier within <FILE_KEY> tags.

```
看起来之前的PDF文件在这个对话中不可访问了。你能否重新上传Pass2Pass-T的论文？这样我可以：

1. 找到所有表格中的精确数据（guessnum = 1, 5, 10, 1000等）
2. 分析折线图的数据如何利用
3. 详细拆解他的叙事结构和文笔

在你重新上传之前，我先回答你能立即用上的部分：

---

## 关于折线图数据的利用方法

学术论文中，对于只在折线图中呈现、没有精确数字的数据，有几种常见做法：

### 方法1：使用数据提取工具（最推荐）
用工具从PDF图片中提取近似数值：
- **WebPlotDigitizer**（https://automeris.io/WebPlotDigitizer/）—— 免费在线工具，最常用
- **PlotDigitizer**
- **Engauge Digitizer**

操作流程：
1. 截图折线图
2. 上传到WebPlotDigitizer
3. 标定坐标轴（告诉工具x轴和y轴的刻度）
4. 点击折线上的数据点
5. 导出近似数值

**在论文中的写法**：
> "Results of [Pass2Pass-T] at guess numbers not reported in their tables are estimated from figures in their paper using WebPlotDigitizer [citation]."

这是完全合规的做法，很多论文都这么干。

### 方法2：只对比有精确数字的点
如果你不想引入近似误差，就只在表格中对比有精确数字的guessnum（1, 5, 10, 1000），折线图部分只做定性对比（"our method consistently outperforms / is comparable to..."），不给具体数字。

### 方法3：联系作者要数据
你已经发邮件申请数据集了，可以顺便问一下能否提供折线图的原始数据。

**我的建议**：用方法1（WebPlotDigitizer）+ 方法2结合。表格对比用精确数字，折线图对比用提取的近似值画你自己的图，两种图都放。

---

请重新上传Pass2Pass-T的论文，我来帮你：
1. 列出所有可以直接引用的精确数据点
2. 标记哪些数据需要从折线图提取
3. 详细拆解他的叙事结构，给你一个可以模仿的写作框架
```

**user**: 

```
这是论文的内容
```

Attachments:
- 978-3-032-07894-0_12.pdf

**assistant**: 

```


让我先完整阅读这篇论文。
```

Tool Call: read_file (state: result)
Args:
  {
    "fileKey": "file:/home/10357289/下载/978-3-032-07894-0_12.pdf-817863-1770607079322",
    "lineOffset": 100,
    "maxLines": 500
  }
Result:
  {
    "fileKey": "file:/home/10357289/下载/978-3-032-07894-0_12.pdf-817863-1770607079322",
    "content": "   101\tthis setting. Pal et  al.  [ \n   102\t16] propose a straightforward round-robin strategy, which \n   103\tapplies a single-leak model (e.g., Pass2Path) to each available leaked password \n   104\tin  turn  and  interleaves  the  resulting  guess  lists.  However,  neither  their  study \n   105\tnor subsequent work has evaluated the practical performance of the round-robin \n   106\tstrategy.  Xiu  and  Wang  [ \n   107\t21]  proposed  MSPointerGuess,  a  multi-leak  password \n   108\tmodel  designed  to  combine  clues  from  multiple  leaked  passwords.  MSPointer-\n   109\tGuess encodes leaked passwords from each website using separate encoders that\n   110\t226F. Huang et al.\n   111\tshare  only  architecture  but  not  parameters,  and  then  employs  a  learnable  soft \n   112\tgate to dynamically determine the information drawn from each source. \n   113\tDespite  these  advancements,  MSPointerGuess  [ 21]  faces  significant  limita-\n   114\ttions. In multi-leak settings, the number of leaked passwords for each user and \n   115\ttheir source websites vary widely. Consequently, requiring a distinct encoder for \n   116\teach leaked password severely hinders the model’s scalability. Even with shared \n   117\tencoder  architecture,  this  design  implies  a  rigid  model  structure  that  must  be \n   118\tspecifically  tailored  or  trained  for  each  distinct  number  of  leaked  passwords  a \n   119\tuser  possesses.  This  makes  it  poorly  adaptable  to  the  wide  variability  in  leak \n   120\tcounts observed in real-world scenarios, thereby limiting its practical applicabil-\n   121\tity and effectiveness. \n   122\tOur  Contributions \n   123\tIn  this  paper,  we  focus  on  multi-leak  scenarios  and  aim  to  build  a  probability \n   124\tmodel  that  accurately  captures  the  similarity  among  multiple  passwords  from \n   125\tthe same user for password guessing. \n   126\tWe  propose  Pass2Pass-T,  a  Transformer-based  [ 19]  password  probability \n   127\tmodel, for predicting a target password from one or multiple leaked passwords \n   128\tof the same user. Fundamentally, it operates by concatenating leaked passwords \n   129\tinto a single sequence which is then fed into the Transformer for guess genera-\n   130\ttion. Recognizing that these concatenated password sequences differ from natural \n   131\tlanguage in three key aspects: their semi-structured nature, high repetitiveness, \n   132\tand lack of typical syntax, we introduce several adaptations. First, we refine the \n   133\tpositional encoding by introducing a segment-wise scheme tailored to password \n   134\tsequences.  For  data  augmentation,  we  also  apply  epoch-level  random  shuffling \n   135\tof  leaked  passwords.  Second,  departing  from  common  tokenization  techniques, \n   136\twe  propose  a  repetition-aware  compression  scheme  to  represent  the  relation-\n   137\tships  among  leaked  passwords  more  clearly  and  concisely.  Finally,  we  leverage \n   138\ttransfer  learning  by  pre-training  on  extensive  single-leak  data  and  fine-tuning \n   139\ton comparatively smaller multi-leak data. \n   140\tWe evaluate existing models under single-leak and multi-leak scenarios. \n   141\tIn the single-leak  scenario, where the attacker holds exactly one leaked pass-\n   142\tword per user, our method achieves a 4.46% attack-success advantage over the \n   143\tbest models at the 10\n   144\t7\n   145\t-guess mark. \n   146\tIn the multi-leak  scenario, where the attacker has access to multiple leaked \n   147\tpasswords per user, our method surpasses previous state-of-the-art methods: it \n   148\tcompromises  4.87%  of  user  accounts  on  the  first  guess—a  7.27×  improvement \n   149\tover the best prior multi-leak attack—and breaks 16.36% of accounts within the \n   150\tfirst five guesses, a 58.9% relative gain. We provide the first systematic empirical \n   151\tevaluation  of  round-robin  guessing,  comparing  it  directly  with  our  multi-leak \n   152\tmodel. \n   153\tTo summarize, we mainly have the following contributions. \n   154\t– We  focus  on  multi-leak  scenarios,  propose  Pass2Pass-T,  to  predict  a  target \n   155\tpassword based on several leaked passwords from the same user. Our model\n   156\tPersonalized Password Guessing227\n   157\tmainly leverage Transformer and enhances it with input compression and seg-\n   158\tmented  positional  encoding,  tailored  to  the  distinct  characteristics  of  pass-\n   159\tword sequences unlike natural language texts. \n   160\t– We  evaluate  Pass2Pass-T  and  show  it  outperforms  existing  attacks  in  both \n   161\tmulti-leak scenarios and single-leak scenarios. \n   162\t– Our multi-similarity model adapts to an arbitrary number of leak passwords, \n   163\twhereas MSPointerGuess requires training and testing on a fixed number of \n   164\tleak passwords. \n   165\t2  Related  Work \n   166\t2.1  Password  Reuse  Behaviors \n   167\tDue to cognitive limitations, users frequently reuse or only slightly modify pass-\n   168\twords across different online services. Florencio and Herley [ \n   169\t5] first documented \n   170\tthe widespread prevalence of password reuse and weak passwords in a large-scale \n   171\tuser  study  in  2007;  later,  Das et  al.  [ \n   172\t4]  corroborated  these  findings  using  web-\n   173\tsite  data  at  NDSS’14.  Subsequent  studies,  such  as  Pearman et  al.  [ \n   174\t18],  found \n   175\tthat  passwords  containing  special  characters  or  numbers  are  more  likely  to  be \n   176\treused. These findings highlight the persistent and multifaceted nature of pass-\n   177\tword reuse. \n   178\t2.2  Personalized  Password  Guessing  via  Leaked  Passwords \n   179\tAttackers can exploit users’ habit of reusing or slightly modifying existing pass-\n   180\twords  across  different  websites.  In  2019,  Pal  et  al.  [ \n   181\t16]proposed Pass2Path, \n   182\ta  sequence-to-sequence  model  that  converts  old  passwords  into  sequences  of \n   183\tcharacter-level edits, cracking nearly 48% of accounts within 1,000 guesses. How-\n   184\tever,  it  cannot  capture  the  mutual  influence  among  edit  operations  and  the \n   185\ttransformation  effects  they  produce,  nor  can  it  leverage  popular  password  dic-\n   186\ttionaries.  At  USENIX  Security  2023,  Wang  et  al.  [ \n   187\t20]  introduced  Pass2Edit, \n   188\twhich breaks password transformation into multi-step classification, improving \n   189\tsuccess rates by 43%  over Pass2Path  in the first 100  guesses for  normal  users, \n   190\tand by another 24% when adding a global dictionary. Yet both Pass2Edit  and \n   191\tPass2Path  only perform single-character edits and remove dissimilar pairs dur-\n   192\ting training, limiting their ability to model long-range transformations. In 2024, \n   193\tXiu  and  Wang  [ \n   194\t21]proposed PointerGuess,  which  builds  on  Bahdanau  et  al.’s \n   195\tattention  mechanism  [ \n   196\t1]  and  Long  Short-Term  Memory  (LSTM)  networks  [ 8], \n   197\tand uses a pointer network to jointly model copying old characters and generat-\n   198\ting new ones, supporting both personalized and population-level reuse behaviors \n   199\twithout  external dictionaries,  and further extended it to multi-leak  settings  as \n   200\tMSPointerGuess.\n   201\t228F. Huang et al.\n   202\t3  Multi-leak  Password-Guessing  Attack \n   203\tIn this section, we introduce the data processing methods and analyze the pass-\n   204\tword reuse behavior and characteristics of passwords across multiple accounts. \n   205\tBased on this analysis, we propose our model, Pass2Pass-T. \n   206\t3.1  Dataset  Collection  and  Pre-Processing \n   207\tWe use the RMDC email aggregation dataset as multi-leak data. Originally, it \n   208\twas a password vault dataset covering aggregated data from 28 sites, with each \n   209\tuser having a different number of leaks. \n   210\tTerminology.    This paper directly employs the RMDC dataset that is released \n   211\tin work [ \n   212\t2]. To familiarise readers with its properties, we briefly summarise the \n   213\tmain cleaning steps below. \n   214\tData  Source  and  Preprocessing.    The raw RMDC archive (182 sites, about \n   215\t427GB)  was  collected  from  public  hacker  forums.  We  keep  only  28  plain-text \n   216\tdump  files  and  apply  three  sequential  filters:  (i)  remove  passwords  containing \n   217\tnon-printable  ASCII  characters;  (ii)  retain  entries  whose  user-name  length  is \n   218\t≥ 3 and password length is 4–25; (iii) require the e-mail field to contain the “@” \n   219\tsymbol. \n   220\tAggregation  Strategy.    After  cleaning,  they  aggregate  accounts  by  e-mail \n   221\taddress  rather  than  user  name.  This  prevents  extremely  common  user  names \n   222\t(e.g. “abc”) from merging passwords belonging to different individuals into the \n   223\tsame  vault,  which  would  otherwise  contaminate  cross-user  data.  Although  e-\n   224\tmail aggregation can occasionally split a single user’s credentials across multiple \n   225\tvaults,  its  impact  on  subsequent  evaluation  is  smaller  than  that  of  user-name \n   226\taggregation. \n   227\tFull  details  can  be  found  in  the  paper  [ 2].  The  dataset  and  preprocessing \n   228\tscripts are available at \n   229\thttps://zenodo.org/records/15646753. \n   230\t1\n   231\t3.2  Password  Reuse  Behaviors \n   232\tBeyond the single-password–reuse behavior noted in prior work [ 16,20], there are \n   233\talso significant or potential relationships between multiple passwords of a user. \n   234\tWe show examples of these relationships in Table \n   235\t1. For some passwords, users \n   236\tsimply reuse strings from different previous passwords. For example, in Exam-\n   237\tple 1, “xslfly” and “512” come from “xslfly118” and “1990512” respectively. In \n   238\taddition to direct password reuse, there is also latent information between mul-\n   239\ttiple passwords. For instance, in Example 7, “B4cp7eii” and “Bcpeiim” exhibit \n   240\ta corresponding relationship. \n   241\tAdditionally,  passwords  from  the  same  user  are  often  highly  repetitive  and \n   242\tsyntax-free. As shown in Examples 3 and 4, strings like “1995622” and “282026” \n   243\tappear  repeatedly  within  the  passwords.  In  Examples  2  and  8,  even  though \n   244\tpasswords like “B4cp7eii” and “Bcpeiim”, as well as “mar1na” and “mari”, are \n   245\tsimilar, they exhibit flexibility in their expression.\n   246\t1 \n   247\tthe dataset requires an ethics-compliance application \n   248\tPersonalized Password Guessing229\n   249\tTable  1.  Typical examples of similarity among multiple passwords \n   250\tReuse TypeNo. Leak passwordTarget \n   251\tPassword segment concatenation 11990512xslfly11819905121990512xslfly512 \n   252\t2mar1nabill1950chick1968 mari03mar1na03 \n   253\t3199562219956221995622dengbinjunjun1995622 \n   254\t4denglei1112 282026282026282026deng282026 \n   255\tConsidering users’ reuse habits56sasha6sasha66sasha00022 sasha666500022sasha \n   256\t6131192Julio92juliojulio100julio100 \n   257\t7mamzeljaMamzelja7f074b7F074b47f074b4 \n   258\t8B4cp7eiiBcpeiim1910 eleon1910 1910Bcpeiim B4cp7eiim \n   259\tNote:  All  displayed  passwords  have  been  anonymized  and  rewritten  to  protect  user \n   260\tprivacy. \n   261\t3.3  Multi-password  Model \n   262\tWe made some simple adaptations to password data based on Transformer [ 19] \n   263\tand  constructed  the  Pass2Pass-T  model,  which  is  a  multi-leakage  password \n   264\tmodel. The choice of Transformer is due to its prominence in natural language \n   265\tprocessing, where password generation can be seen as a character-level language \n   266\tmodeling task, and Transformer is the mainstream model for this task. For the \n   267\tmulti-leak  scenario,  we  concatenate  all  leaked  passwords  of  the  same  account \n   268\twith <sep>  into  a  single  sequence,  compress  it  with  a  dedicated  strategy,  and \n   269\temploy  a  decoder-only  Transformer   [ \n   270\t19]  for  autoregressive  modeling  to  fully \n   271\texploit its long-context capacity and high training throughput. We adapted to \n   272\tthe data characteristics of multiple password sequences. \n   273\tInput  Data  Handling  Strategies.  We considered three processing methods, \n   274\tof which the first two have already been tried in password processing, while the \n   275\tthird is a new strategy we propose. \n   276\t1) BPE  subword  segmentation: BPE subword segmentation is a mainstream app-\n   277\troach in NLP. However, passwords are morphologically diverse, and the same \n   278\tsemantic fragment may appear in many spellings (e.g., p@ssword, Pa55word, \n   279\tp4w0rd),  yielding  non-unique  tokenization  paths  and  unstable  Monte-Carlo \n   280\testimates at high guess ranks. \n   281\t2) Keyboard-mapping:  Following  Pass2Edit  /  Pass2Path,  each  character  is \n   282\tmapped  to  its  US-keyboard  coordinate  to  shorten  edit  sequences.  This \n   283\tchiefly benefits edit-distance models (e.g., transforming abcdefg  to ABCDEFG \n   284\tneeds only one <CAP>  insertion). Our experiments show negligible impact on \n   285\tcharacter-level generators. \n   286\t3) Repetition-aware  compression: When the current password is identical to any \n   287\tprevious  one in the same account, we replace the entire string with a pointer \n   288\tsymbol  <s \n   289\tj>,  where j  denotes  the  position  of  its  first   occurrence  in  the \n   290\tsequence. For example, if the 3rd password repeats the 1st, we encode it as \n   291\t<s \n   292\t1>.  This  compression  shortens  the  input  and  improves  performance,  so\n   293\t230F. Huang et al.\n   294\tPass2Pass-T  adopts  it.  Under  credential-stuffing  defenses,  repetition-aware \n   295\tcompression markedly boosts top-5 success rates (see Table \n   296\t5). \n   297\tSegment-Wise  Positional  Encoding.  The vanilla sinusoidal positional encod-\n   298\ting presumes a globally monotonically increasing index, which multi-leak inputs \n   299\tobviously  violate.  We  therefore  reset  the  positional  index  at  every  password \n   300\tboundary  and  append  a  one-hot  segment  tag  to  avoid  spurious  inductive  bias. \n   301\tConcretely,  within  each  password  we  keep  the  original  Transformer  sin–cos \n   302\tencoding,  while  across  passwords  we  add  a  one-hot  vector  to  distinguish  seg-\n   303\tments,  as  illustrated  in  Fig. \n   304\t2.  During  training,  we  randomly  shuffle  the  order \n   305\tof  password  blocks  at  the  epoch  level  to  weaken  the  model’s  dependence  on  a \n   306\tpseudo-timeline. \n   307\tFig.  2.  Segment Level embedding \n   308\tPre-training.  A large corpus of single-password samples enhances brute-force \n   309\tcapacity; we pre-train on it and fine-tune on multi-password data, enabling the \n   310\tmodel to learn cross-password similarities. \n   311\tIn sum, by combining repetition-aware compression, segment-wise positional \n   312\tencoding, and pre-training, Pass2Pass-T captures multi-password reuse patterns \n   313\tmore accurately. \n   314\t3.4  Monte-Carlo  PPSM \n   315\tWe propose to pre-sample password-similarity trajectories offline so that a newly \n   316\tentered  password  could  be  scored  with  a single  forward  pass.  While  attractive \n   317\tfor small candidate sets on compute-rich devices, the overall cost would still scale \n   318\tas O(n\n   319\t2\n   320\t) with the number n  of stored passwords, and quantifying this trade-off \n   321\tis left for future experiments. \n   322\t4  Empirical  Evaluation \n   323\tWe  evaluate  our  model  in  two  single-leak  attack  scenarios  and  six  multi-leak \n   324\tattack scenarios (when the number of given passwords is one, our model auto-\n   325\tmatically  degenerates  to  the  single-leak  model,  so  we  include  that  scenario  as \n   326\twell). Next, we assess the performance of our similarity model under high guess \n   327\tcounts to reflect the threat of offline attacks, which prior work has not revealed. \n   328\tFinally,  we  perform  ablation  studies  to  demonstrate  the  contribution  of  each \n   329\tcomponent to the model’s performance.\n   330\tPersonalized Password Guessing231\n   331\t4.1  Experimental  Setting \n   332\tFor the multi-similar experiment settings, We chose RMDC because we regard \n   333\tMSPointerGuess’s multi-leak setting as unrealistic: their attacker knows at most \n   334\ttwo historical passwords per user, both taken from only two identical datasets. \n   335\tTherefore, their setting diverges sharply from real-world conditions—where the \n   336\tnumber of leak passwords per user varies and originates from diverse sites—and \n   337\tcannot faithfully reflect the true threat landscape. \n   338\tWe  follow  the  experimental  setup  of  Pass2Path  [ 16].  We  evaluate  the \n   339\tattacker’s  capabilities  when  they  know  different  numbers  of  passwords,  under \n   340\ttwo  conditions:  one  where  direct  reuse  of  leak  passwords  is  removed  (referred \n   341\tto as  “no repeat” hereafter) and  one  where  it is  not . Additionally,  we  set dif-\n   342\tferent  numbers  of  leak  passwords  for  the  attacker  to  reflect  the  impact  of  leak \n   343\tpasswords on the success rate of account compromise. \n   344\tFor  the  multi-leak  experiments  we  use  the  RMDC  dataset  and  adopt  the \n   345\tPass2Path [ \n   346\t16] evaluation protocol. We vary the number of leak passwords avail-\n   347\table to the attacker  and compare their  success against  two site configurations: \n   348\twith and without credential-stuffing protection. \n   349\tSpecifically,  we  use  the  other  passwords  to  predict  the  final  password.  To \n   350\tcontrol input length, we truncate each record to the first six passwords. The last \n   351\tpassword  in  the  truncated  list  is  used  as  the  attack  target,  and  the  preceding \n   352\tentries serve as leak inputs. \n   353\tIn  this  chapter,  we  use Leak  Num  to  denote  the  number  of  passwords  the \n   354\tattacker possesses. \n   355\t– ≥ 1  scenario—keep the original RMDC distribution and treat the last pass-\n   356\tword of each account as the prediction target. \n   357\t– ≥ 2  scenario—select  accounts  with 3–6   passwords,  using  the  first n−1to \n   358\tpredict the n-th. \n   359\t– =5 scenario—select  accounts  with 6–10   leaked  passwords  and  retain  the \n   360\tfirst six (i.e., five leak plus one to predict). \n   361\tThe  “≥ 1”  bucket  preserves the dataset’s  natural  distribution,  whereas the \n   362\t“≥  2”  and  “=  5”  buckets  simulate  moderate  and  severe  leakage  conditions, \n   363\trespectively, enabling us to evaluate attack accuracy under different leakage lev-\n   364\tels. \n   365\tWe  used  the  RMDC  open-source  7  million  data,  with  90%  as  the  training \n   366\tset, and the remaining 10% was filtered using the method mentioned earlier to \n   367\textract 10,000 samples from each of the 6 scenarios for testing. \n   368\tHyperparameter  Settings.  For our model, we configured the model dimensions to \n   369\t512, employed 8 attention heads and 8 layers, set a dropout rate of 0.1, limited \n   370\tthe  maximum  sequence  length  to  128  tokens,  used  a  training  set  ratio  of  0.95, \n   371\ttrained for 15 epochs, and applied gradient accumulation with 2 steps. We used \n   372\ta batch size of 128. This arrangement was chosen because the loss had essentially \n   373\tconverged by the 15th epoch. \n   374\tRegarding the training strategy, we adopted a learning rate of 1e-4, a warmup \n   375\tof 1000, and a cosine annealing learning rate.\n   376\t232F. Huang et al.\n   377\tFor  the  Pass2Edit \n   378\t2\n   379\tand  Pass2Path  models,  we  follow  the  original  data \n   380\tpipeline and train on the similar password pairs. \n   381\t3\n   382\tIn terms of pair count, our new \n   383\tdataset  is  comparable  to  4iQ.  Since  we  observed  that  validation  loss  continues \n   384\tto decrease beyond three epochs, for a fair comparison we also train Pass2Edit \n   385\tfor 15 epochs and save the checkpoint with the lowest validation loss. \n   386\tFor  our  model,  we  pre-trained  for  1.5  days  on  two  RTX  3090  GPUs  (using \n   387\t10% of the merged single-password dataset) and then fine-tuned for 0.6 days on \n   388\ta single RTX 3090. \n   389\t4.2  Ethical  Considerations \n   390\tThis  dataset  has  been  widely  disseminated  through  BitTorrent  (BT).  In  our \n   391\tstudy, it is used solely to advance password protection technologies rather than \n   392\tto inflict further harm. \n   393\tWe treat each password as confidential during processing; no real user pass-\n   394\twords  appear  in  this  paper,  and  all  displayed  passwords  are  edited  variants  of \n   395\tthe  originals.  Access  to  the  data  is  restricted  to  the  participants  of  this  study, \n   396\tand authentication via certificates is required. \n   397\t4.3  Estimation  for  Crack  Rate \n   398\tThe optimal strategy for password guessing is: to  strictly  attempt  all  candidate  pass-\n   399\twords in descending order of model probability. However, sampling probabilities that \n   400\tstrictly decrease monotonically from the model is impractical, so estimation meth-\n   401\tods are needed. We use Beam Search and Monte Carlo methods for evaluation. \n   402\tBeamSearch  explicitly enumerates and attacks the k  = 1 000 highest-probability \n   403\tpasswords  generated  by  the  model.  It  has  been  adopted  in  prior  work  such  as \n   404\tPass2Path, Pass2Edit, and PointerGuess [ \n   405\t16,20,21]. Its exhaustive nature, how-\n   406\tever, makes evaluation at very large guess budgets computationally prohibitive. \n   407\tMonte  Carlo  is a statistical estimator that samples passwords from the model \n   408\tand  applies  inverse-probability  weighting,  yielding  an  unbiased  estimate  of  the \n   409\tcrack rate even at extremely high guess counts. \n   410\t4.4  Experimental  Results  in  Multi-leak  Attack  Scenarios \n   411\tWe first employed Beam Search to evaluate performance with a low number of \n   412\tguesses.  We  observed  that,  under  such  conditions,  our  model  exhibits  a  signif-\n   413\ticant  improvement  in  accuracy  within  the  first  100  attempts—particularly  on\n   414\t2 \n   415\tPass2Edit [\n   416\t20] was not open-sourced, we reimplemented the method described in the \n   417\tpaper.  We  evaluated  our  implementation  under  the  original  authors’  experimental \n   418\tScenario 1; the results are shown in Table \n   419\t2. Our reproduction yields results approx-\n   420\timately  1%  higher  than  those  reported  in  the  original  work,  with  the  discrepancy \n   421\twithin an acceptable margin, indicating that the reproduction is essentially accurate. \n   422\t3 \n   423\tIn the previous paper, approximately 116 million password pairs from the 4iQ dataset \n   424\twere  used  for  training.  Applying  the  Pass2Edit  filtering  algorithm  to  10%  of  that \n   425\tdata produced 112 million pairs. \n   426\tPersonalized Password Guessing233\n   427\tTable  2.  Crack Rate in Multi-Leak Scenarios \n   428\tLeak \n   429\tnum \n   430\tGuess \n   431\tnum \n   432\tFLA  [\n   433\t12\n   434\t] \n   435\tPass2Edit \n   436\t[\n   437\t20\n   438\t] \n   439\tPass2Path \n   440\t[\n   441\t16\n   442\t] \n   443\tPointerGuess \n   444\tTransformer \n   445\tPass2Pass-\n   446\tT \n   447\t≥ 1 \n   448\t12.59%43.51%43.51%46.26%47.03%47.23% \n   449\t52.98%55.65%55.23%56.32%57.41%57.61% \n   450\t103.68%56.95%56.29%57.47%58.68%58.91% \n   451\t1005.94%60.29%58.22%60.72%61.88%62.00% \n   452\t10008.44%63.26%59.61%62.88%64.37%64.67% \n   453\t10\n   454\t7 \n   455\t40.49%\\\\76.27%79.25%79.40% \n   456\t≥ 2 \n   457\t12.76%49.11%48.34%54.38%55.34%55.95% \n   458\t53.20%67.18%67.84%68.25%69.65%69.81% \n   459\t103.79%68.65%69.08%69.62%71.09%71.27% \n   460\t1006.12%72.07%71.14%72.72%73.96%74.02% \n   461\t10008.76%74.94%72.40%74.81%76.02%76.18% \n   462\t10\n   463\t7 \n   464\t41.30%\\\\83.65%85.95%86.43% \n   465\t=5 \n   466\t13.25%45.03%45.13%57.02%58.50%59.70% \n   467\t54.11%74.60%76.98%76.02%78.58%78.89% \n   468\t104.76%77.00%78.90%78.21%80.63%80.84% \n   469\t1007.12%80.81%81.09%81.87%83.17%83.29% \n   470\t10009.65%83.58%82.09%83.48%84.35%84.43% \n   471\t10\n   472\t7 \n   473\t37.42%\\\\88.68%89.80%89.96% \n   474\t≥ 1 \n   475\t(no \n   476\trepeat) \n   477\t12.17%0.73%0.61%1.00%1.08%1.27% \n   478\t52.95%11.08%7.87%10.82%12.38%12.74% \n   479\t103.16%13.12%9.88%12.99%15.01%15.34% \n   480\t1004.90%18.61%13.95%19.07%21.08%21.40% \n   481\t10007.34%23.83%16.51%23.45%26.19%26.71% \n   482\t10\n   483\t7 \n   484\t36.94%\\\\49.89%   56.99%56.84% \n   485\t≥ 2 \n   486\t(no \n   487\trepeat) \n   488\t12.67%0.18%0.23%0.69%1.12%1.98% \n   489\t53.18%10.92%7.27%9.76%12.75%13.48% \n   490\t103.67%14.19%10.96%13.49%17.00%17.49% \n   491\t1005.89%21.82%16.71%22.07%24.93%25.39% \n   492\t10008.47%27.90%20.52%27.16%30.54%31.21% \n   493\t10\n   494\t7 \n   495\t38.84%\\\\53.03%59.87%60.48% \n   496\t=5 \n   497\t(no \n   498\trepeat) \n   499\t12.93%0.18%0.24%0.67%2.02%4.87% \n   500\t53.92%9.64%4.95%8.39%13.58%16.36% \n   501\t104.28%15.84%12.38%13.57%21.02%21.99% \n   502\t1007.21%25.95%21.54%26.02%31.54%32.01% \n   503\t10009.93%33.49%26.52%32.59%36.49%36.93% \n   504\t10\n   505\t7 \n   506\t39.44%\\\\53.35%58.70%59.33% \n   507\tNote:   Bolded  entries  indicate  the  best-performing  model  when  attacking \n   508\tbased on leaked passwords. \n   509\t234F. Huang et al. \n   510\t(a) Leak  Num1(b) Leak  Num2(c) Leak  Num  =  5 \n   511\tFig.  3. Attack Success Rate within the Top 1,000 Guesses on the Repeat Multi-Leak \n   512\tAttack Scenarios \n   513\t(a) Leak  Num1(b) Leak  Num2\n   514\t(c) Leak  Num  =  5 \n   515\tFig.  4. Attack Success Rate within the Top 1,000 Guesses on the No-Repeat Multi-\n   516\tLeak Attack Scenarios \n   517\tthe very first guess. The results are shown in Figs. 4, 3, and Table 2.Onthe very \n   518\tfirst guess, our method cracked 4.87% of accounts, revealing that round-robin \n   519\tattacks severely underestimate an attacker’s early-stage cracking power. \n   520\tIn the repeat scenario, when attackers possess more than five Leak passwords, \n   521\tour\n   522\t method—compared to the best previous approach—increases the first-guess \n   523\tsuccess rate from 57.02% to 59.70%. In the no-repeat scenario, the success rate \n   524\timproves from 0.67% to 4.87%, representing a 7.27-fold increase. \n   525\tWe observe that although PointerGuess is the most recent model, its actual \n   526\tattac\n   527\tk performance in multi-leak scenarios is worse than that of the round-robin-\n   528\tbased Pass2Edit. We speculate that this performance gap stems from the archi-\n   529\ttectural design of PointerGuess, which first generates multiple separate password \n   530\tdistributions and only combines them at the final stage. As a result, interactions \n   531\tbetween different Leak passwords occur too late in the process, making it difficult \n   532\tfor the model to capture cross-password dependencies effectively. \n   533\tIn addition, we find it achieves better first-guess accuracy than its round-\n   534\trobin\n   535\t variant but loses this advantage by the 10th guess, indicating limited gen-\n   536\teralization (see Appendix B for details). \n   537\tOur analysis reveal that, compared to our multi-leak model, the single-leak \n   538\tmo\n   539\tdel tends to directly reuse passwords on the first attempt (unlike Pass2Edit, \n   540\twhere we did not force the first guess to be a reuse; otherwise, the first-guess \n   541\tsuccess rate would be zero) due to the lack of additional user information. In \n   542\tPersonalized Password Guessing235 \n   543\tcontrast, our multi-leak model enables the attacker can infer the user’s password \n   544\thabits, whether they tend to reuse passwords or make slight modifications. \n   545\t4.5  Result  Analyze \n   546\tTable  3. Comparison examples of single-leak and multi-leak attacks: top 5 and top \n   547\t31–40 \n   548\tLeak \n   549\tpw\n   550\tgurgled123 \n   551\tsparkie123 \n   552\thouxiaochao \n   553\txiaochao521 \n   554\tB4cp7eii \n   555\tBcpeiim1910 \n   556\t191991 \n   557\teleon1910 \n   558\t1910Bcpeiim \n   559\tTargetsalle123houxiaochao521173232 \n   560\tRankPass2EditOursPass2EditOursPass2EditOurs \n   561\t1gurgled123sparkie123houxiaochao xiaochao521B4cp7eiiB4cp7eiim \n   562\t2\n   563\tsparkie123gurgled123xiaochao521 houxiaochaoBcpeiim1910B4cp7eii \n   564\t3\n   565\tgurgledgurgled123456xiaochao191991b4cp7eii \n   566\t4\n   567\tsparkiesparkiexiaochao52xiaochao52eleon1910eleon1910 \n   568\t5\n   569\tgurgled1sparkie12houxiaochao1 houxiaochao521 1910bcpeiimEleon1910 \n   570\t... \n   571\t31gurgled23gurgled13163.comhouxiao5211910acpeiEleon191 \n   572\t32\n   573\tsparkie2123gurgledhouchaoxiaochao521.Acp7eii19191991 \n   574\t33\n   575\tgurgled12345 neopets123a123456houxiaochao019911991Bcpeiim191 \n   576\t34\n   577\tsparkie14love1231314521xiaochao521521eleon10123456 \n   578\t35\n   579\tGurgledspark12313145205201314a1cp7eii1991Eleon \n   580\t36\n   581\tsparkie12345 dragon123woainiXiaochao521BCPEIIM1910 B4cp7eiim1910 \n   582\t37\n   583\tsparkie01sparkie12345 houda7758521111111191910 \n   584\t38\n   585\tgurgled14princess123 xiaochao521. woainiB4cp7eii4cp7eiim \n   586\t39\n   587\tSparkiesparkie101houxiaochao2 houxiaochaBcpeiim191eleon1991 \n   588\t40\n   589\tgurgled2gurgled22chao521hdchao521191991a1991bcpeiim \n   590\tFor our example, we selected the Pass2Edit + round-robin scheme—shown to achieve \n   591\tthe best empirical attack performance among earlier methods—rather than the more \n   592\trecent MSPointerGuess. \n   593\tIn the no-repeat scenario, with 100 guesses and five leak passwords, our multi-\n   594\tleak model still delivers an improvement of nearly 5.99% in success rate, which \n   595\tis 23.02% higher compared to Pass2Edit. As presented in Table 3, for select data \n   596\tsamples\n   597\t with such improvements, we examined both the first five attack attempts \n   598\tand the list of attacks from the 31st to the 40th guesses. \n   599\tWe found that our multi-leak model can capture the intrinsic relationships \n   600\tamong",
    "lineOffset": 100,
    "linesRead": 500,
    "totalLines": 955
  }

Tool Call: read_file (state: result)
Args:
  {
    "fileKey": "file:/home/10357289/下载/978-3-032-07894-0_12.pdf-817863-1770607079322",
    "lineOffset": 600,
    "maxLines": 355
  }
Result:
  {
    "fileKey": "file:/home/10357289/下载/978-3-032-07894-0_12.pdf-817863-1770607079322",
    "content": "   601\t samples to launch more precise attacks. For instance, when “gurgled123” \n   602\tand “sparkie123” are leak passwords, the single-leak plus round-robin method \n   603\ttypically generates numerous variants of “gurgled” and “sparkie”—as observed \n   604\tin the 31st to 40th guesses—whereas our multi-leak model identifies common \n   605\tpatterns across the passwords, attempting to break the password pair using \n   606\t236F. Huang et al. \n   607\t(a) Leak  Num1(b) Leak  Num2\n   608\t(c) Leak  Num  =  5 \n   609\tFig.  5. Comparative experiments with the state-of-the-art no-leak attack FLA under \n   610\tthe no-repeat scenario \n   611\tstrategies such as combining an English word with “123”. In the second example, \n   612\ta simpler cross-password reuse is observed by concatenating “521” from the \n   613\tleak passwords “houxiaochao” and “xiaochao521”, which allowed our multi-leak \n   614\tmodel to break the password in just 5 guesses. \n   615\tIn the third example, where a greater number of leak passwords are available, \n   616\tthe\n   617\t model deduced the target password on the very first guess. It inferred that \n   618\tthe relation between “Bcpeiim” and “B4cp7eiim” involves the insertion of two \n   619\tdigits within “Bcpeiim”, and, taking into account previous accounts suggesting \n   620\tthat users might avoid directly reusing passwords, it opted for a combination \n   621\tstrategy. \n   622\t4.6  Advantage  of  Multi-Leak  Attacks  Under  High  Guess  Numbers \n   623\tWe refer to attacks that do not rely on leaked passwords as no-leak  attacks. \n   624\tIn\n   625\t previous research, only Pass2Path compared single-leak  attacks and no-leak \n   626\tattacks. Since it did not consider non-similar passwords, their experimental \n   627\tresults showed that after 100,000 guesses, the single-leak attack had no advan-\n   628\ttage over the no-leak attack. \n   629\tIn contrast, our model, during training, learns from less similar password \n   630\tpairs.\n   631\t Using the Monte Carlo method for evaluation, we found, contrary to previ-\n   632\tous conclusions, that under almost all guess numbers, the performance of no-leak \n   633\tattacks is worse than that of multi-leak attacks. \n   634\tWe find that the primary advantage comes from samples that exhibit partial \n   635\tsimilarit\n   636\ty combined with enumerative patterns. In such cases, the model can \n   637\tleverage partial similarity information to achieve orders-of-magnitude improve-\n   638\tments in attack success rates. See Table 4. \n   639\tSince Pass2Edit and Pass2Path are edit-based—where a single password cor-\n   640\tresp\n   641\tonds to multiple generation paths and accurate probability computation is \n   642\tinfeasible—we did not include them in the high-guess-count evaluation (Fig. 5). \n   643\tPersonalized Password Guessing237 \n   644\tTable  4. Attack Results of Different Methods on Two Target Passwords \n   645\tTarget \n   646\tpw \n   647\tzq534126514fadednegro33 \n   648\tMethodFLA [12] Pass2Pass-T Pass2Pass-T FLA [12] Pass2Pass-T Pass2Pass-T \n   649\tLeak \n   650\tpw \n   651\t\\\\wangqi890519 \\\\domything33 \n   652\tRank8.48e+11 4.78e+119.60e+93.84e+14 4.51e+132.10e+12 \n   653\tTable  5. Ablation experiment results (percentage) \n   654\tGuess \n   655\tnum \n   656\tPass2Pass-T \n   657\t(Transformer \n   658\t+zip \n   659\tpw \n   660\t+new \n   661\tpos finetune) \n   662\tTransformer \n   663\t+zip \n   664\tpw \n   665\tTransformer Transformer \n   666\tsspm \n   667\tPass2Edit \n   668\t[\n   669\t20] \n   670\tAblation \n   671\tVariants \n   672\torgABCD \n   673\tLeak Num =5 and no repeat \n   674\t14.87%4.22%2.02%0.22%0.18% \n   675\t516.36%15.25%13.58%6.80%9.64% \n   676\t1021.99%20.64%21.02%17.37%15.84% \n   677\t10032.01%31.50%31.54%29.90%25.95% \n   678\t100036.93%36.72%36.49%35.53%33.49% \n   679\t4.7  Ablation  Study \n   680\tIn order to validate the impact of the methods proposed in this paper, we \n   681\tdesigned\n   682\t a series of ablation experiments. Specifically, based on the complete \n   683\tmodel, we individually removed the following key factors, as shown in Table 5: \n   684\tA) Removal of the new positional encoding and pretraining strategy; \n   685\tB) Disabling the compression strategy; \n   686\tC) Replacing the multi-leak method with standard round-robin; \n   687\tD) Replacing the Transformer module with the Pass2Edit model. \n   688\t4.8  Single-Leak  Scenario  Evaluation \n   689\tIn addition to the multi-leak scenario, we have also evaluated the model’s per-\n   690\tformance\n   691\t under the single-leak scenario. \n   692\tWe conduct two single-leak experiments. Setting A trains on Tianya → \n   693\tDo\n   694\tdonew and is evaluated on Tianya → Taobao. Setting B setup uses 90% \n   695\tof the 7 million data from the RMDC dataset for training, and the remaining \n   696\tportion is filtered to test the cases where Leak  Num = 1 (Table 6). \n   697\t238F. Huang et al. \n   698\tTable  6. Comparison of Results (%) on Two Datasets \n   699\tLeak Num Guess num Pass2Edit [20] PointerGuess [21] Pass2Pass-T \n   700\tSetting  A:  Tianya→Dodonew  (train);  Tianya→Taobao  (test) \n   701\t=1127.28%27.73%26.94% \n   702\t531.10%31.10%31.24% \n   703\t1032.15%31.99%32.26% \n   704\t10034.09%34.20%34.33% \n   705\t100036.40%36.27%36.58% \n   706\t10\n   707\t7 \n   708\t–50.14%52.38% \n   709\tSetting  B:  RMDC  7M  (train);  RMDC  100K  (test) \n   710\t=1140.42%40.21%40.64% \n   711\t546.88%47.05%48.05% \n   712\t1048.19%47.92%49.23% \n   713\t10051.13%51.45%52.41% \n   714\t100053.94%53.55%55.42% \n   715\tUsing the same training and testing setup as Scenario 1 in Pass2Edit—Tianya \n   716\t→ Dodonew for training and Tianya → Taobao for testing—we conduct a fair \n   717\tcomparison between the prior method and ours. We observe no significant per-\n   718\tformance difference, indicating that the previous approach is already sufficient \n   719\tto capture single-password modification patterns within 1,000 guesses. \n   720\t5  Conclusion \n   721\tWe focus on multi-leak scenarios and propose Pass2Pass-T to predict a target \n   722\tpassword from several leaked passwords of the same user. Pass2Pass-T leverages \n   723\tthe Transformer, enhanced with input compression and segmented positional \n   724\tencoding tailored to passwords. This design enables Pass2Pass-T to outperform \n   725\texisting methods in both single-leak and multi-leak scenarios. Additionally, we \n   726\tintroduce a password strength estimator based on Monte Carlo methods, helping \n   727\tusers select appropriate passwords in multi-leak situations. \n   728\tAcknowledgment. This research is supported by National Natural Science Founda-\n   729\ttion of China (No. 62202012 and No. 62072010), BIGC Project Ea202515 and Pub-\n   730\tlishing Think Tank Platform Development Project KYCPT202514. We also thank the \n   731\tanonymous reviewers for their valuable comments and suggestions. \n   732\tPersonalized Password Guessing239 \n   733\tAppendix \n   734\tA  MSPointerGuess  Implement \n   735\tIn the original PointerGuess formulation [ 21], several implementation details \n   736\tare left unspecified, which undermines reproducibility. To address this, we now \n   737\tpresent a complete account of our multi-source PointerGuess implementation. \n   738\tWe noticed an inconsistency in the PointerGuess paper between the calcula-\n   739\ttion\n   740\t of Pg in Eq. 5 and its depiction in Fig. 3. Therefore, we follow the method \n   741\tin\n   742\t Eq. 5 when computing Pg. \n   743\tSecond, although MSPointerGuess defines a multi-source fusion mechanism \n   744\tfor\n   745\t the copy distribution P\n   746\tcopy\n   747\t, it omits any description of how the generation \n   748\tdistribution P\n   749\tvocab \n   750\tis obtained. To fill this gap, we compute individual context \n   751\tvectors C \n   752\t(i) \n   753\tt \n   754\tfor each leaked password, weight each vector by its learned soft-gate \n   755\tscore, and sum them to form a global context C\n   756\tt\n   757\t. We then concatenate C\n   758\tt \n   759\twith \n   760\tthe decoder state s\n   761\tt \n   762\tand project the result to produce P\n   763\tvocab\n   764\t. \n   765\tThird, we observe that Eq. (5) applies two successive linear mappings with-\n   766\tout\n   767\t intervening non-linearities; since such mappings can be algebraically merged \n   768\tinto a single affine transformation, we implement this step using a single fully \n   769\tconnected layer. \n   770\tFinally, We observe that in the original MSPointerGuess design, the number \n   771\tof\n   772\t projection matrices W\n   773\tc \n   774\tequals the number of leak passwords, giving a one-\n   775\tto-one correspondence between each W\n   776\tc \n   777\tand its context vector C\n   778\tt \n   779\t(see Eq. 9 in \n   780\tthe MSPointerGuess paper). In our setting, however, every sample contains a \n   781\tvariable number of leak passwords and the websites are shuffled, so no position \n   782\tconveys extra information. Hence, we train a single global W\n   783\tc \n   784\tto project all C\n   785\tt \n   786\tvectors and reuse the same encoder to encode each password multiple times. \n   787\tB  Comparison  Between  Simple  Round-Robin \n   788\tand  MSPointerGuess  Approaches \n   789\tWe compare three strategies whose results are summarized in Table 7: \n   790\t1. Original  MSPointerGuess: feed the entire set of leak passwords for a user \n   791\tat\n   792\t once; the model computes probabilities for all candidates in a shared con-\n   793\ttext and guesses in descending order of these scores. \n   794\t2. Round-robin: run MSPointerGuess separately on each leak-password \n   795\tsequence,\n   796\t take the current top-scoring candidate from every sequence in turn, \n   797\tand remove duplicates. \n   798\t3. Global  sort: also compute probabilities separately for each sequence, but \n   799\tpoo\n   800\tl all candidates and sort them globally by probability before guessing. \n   801\tIn the leak-num = 5 setting, MSPointerGuess (MSPG) outperforms round-\n   802\trobin\n   803\t in one-guess (top-1) accuracy. However, its performance degrades signifi-\n   804\tcantly under the leak-num = 5 (no-repeat) condition. \n   805\t240F. Huang et al. \n   806\tTable  7. Crack rates of three guessing strategies on the RMDC dataset (percentage) \n   807\tLeak \n   808\tnum \n   809\tGuess \n   810\tnum \n   811\tRound-\n   812\trobin \n   813\t(dedup) \n   814\tGlobal \n   815\tsort\n   816\t \n   817\tMS-\n   818\tPointerGuess \n   819\t≥ 1143.38%43.11%46.26% \n   820\t555.12%56.48%56.32% \n   821\t1056.34%57.70%57.47% \n   822\t100062.76%62.85%62.88% \n   823\t=5144.68%44.76%57.02% \n   824\t571.95%76.83%76.02% \n   825\t1074.21%78.97%78.21% \n   826\t100082.82%83.37%83.48% \n   827\t≥ 1 \n   828\t(no  repeat) \n   829\t10.85%0.87%1.00% \n   830\t510.91%10.93%10.82% \n   831\t1012.83%13.11%12.99% \n   832\t100023.29%23.31%23.45% \n   833\t=5 \n   834\t(no  repeat) \n   835\t10.07%0.21%0.67% \n   836\t57.57%5.61%8.39% \n   837\t1012.21%13.54%13.57% \n   838\t100031.57%32.32%32.59% \n   839\tTo further investigate this phenomenon, we compare the distribution of target \n   840\tpassword repetition rates between the two methods for their first-guess advan-\n   841\ttage samples (i.e., samples where MSPG ranks the correct password higher than \n   842\tround-robin) under the leak-num = 5 setting. The results are shown in Fig. 6: \n   843\t(a) The target password repetition rates of MSPG’s first-guess advantage \n   844\tsamples;\n   845\t \n   846\t(b) The target password repetition rates of the leak-num = 5 test set; \n   847\t(c) The target password repetition rates of the leak-num = 5 (no-repeat) test \n   848\tset.\n   849\t \n   850\tIt can be observed that MSPG’s advantage mainly comes from cases where \n   851\tthe\n   852\t target password appears multiple times in the leak set. When the target \n   853\tpasswords are non-repeating, as in (c), its top-1 success rate drops significantly. \n   854\tThis indicates that MSPG lacks generalization ability under multi-password con-\n   855\tditions with non-repetitive targets. \n   856\tThis limited effectiveness likely results from its origins as a lightweight (0.5 M-\n   857\tparameter)\n   858\t extension of the PointerGuess model, which was originally designed \n   859\tfor single-leak scenarios and thus struggles to capture correlations across multiple \n   860\tleaked passwords. \n   861\tPersonalized Password Guessing241 \n   862\t(a) MSPointerGuess’s \n   863\tfirst  guess  advantage \n   864\tsamples \n   865\t(b) the  leak-num  =  5 \n   866\ttest  set \n   867\t(c) the  leak-num  =  5 \n   868\t(no-repeat)  test  set \n   869\tFig.  6. Target password repetition rate distributions under the leak-num = 5 setting \n   870\tC  Impact  of  the  Estimation  Method \n   871\tMC is slightly more optimistic because it avoids beam-search pruning, as theory \n   872\tpredicts (Table 8). \n   873\tTable  8. Crack rate comparison between Transformer and Pass2Pass-T under different \n   874\testimation methods (percentage form) \n   875\tGuess num Monte Carlo ↑Beam Search ↑ \n   876\tTransformer Pass2Pass-T Transformer Pass2Pass-T \n   877\t1021.09%23.10%21.02%21.99% \n   878\t10031.58%32.39%31.54%32.01% \n   879\t100036.88%37.52%36.49%36.93% \n   880\tReferences \n   881\t1. Bahdanau, D., Cho, K., Bengio, Y.: Neural machine translation by jointly learning \n   882\tto align and translate. In: Proceedings of the International Conference on Learning \n   883\tRepresentations (ICLR) (2015) \n   884\t2. Cheng, H., Huang, F., Yang, J., Li, W., Wang, P.: Practically secure honey pass-\n   885\tw\n   886\tord vaults: new design and new evaluation against online guessing. In: Proceed-\n   887\tings of the 34th USENIX Security Symposium (USENIX Security) (2025) \n   888\t3. Cor, K., Sood, G.: Pwned: How often are Americans’ online accounts breached? \n   889\tarXiv\n   890\t preprint arXiv:1808.01883 (2018) \n   891\t4. Das, A., Bonneau, J., Caesar, M., Borisov, N., Wang, X.F.: The tangled web of \n   892\tpassw\n   893\tord reuse. In: Proceedings of the 21st USENIX Security Symposium (NDSS \n   894\t’14), San Diego, CA, USA (2014) \n   895\t242F. Huang et al. \n   896\t5. Florencio, D., Herley, C.: A large-scale study of web password habits. In: Proceed-\n   897\tings\n   898\t of the 16th International Conference on World Wide Web, WWW ’07, pp. \n   899\t657–666, New York, NY, USA. Association for Computing Machinery (2007) \n   900\t6. Ghorbani Lyastani, S., Schilling, M., Neumayr, M., Backes, M., Bugiel, S.: Is fido2 \n   901\tthe\n   902\t kingslayer of user authentication? A comparative usability study of fido2 pass-\n   903\twordless authentication. In: 2020 IEEE Symposium on Security and Privacy (SP), \n   904\tpp. 268–285 (2020) \n   905\t7. Hanamsagar, A., Woo, S.S., Kanich, C., Mirkovic, J.: Leveraging semantic trans-\n   906\tformation\n   907\t to investigate password habits and their causes. In: Proceedings of the \n   908\t2018 CHI Conference on Human Factors in Computing Systems, CHI ’18, pp. 1–12, \n   909\tNew York, NY, USA. Association for Computing Machinery (2018) \n   910\t8. Hochreiter, S., Schmidhuber, J.: Long short-term memory. Neural Comput. 9(8), \n   911\t1735–1780\n   912\t (1997) \n   913\t9. Hunt, T.: Have I been pwned (2025). https://haveibeenpwned.com \n   914\t10. Ma, J., Yang, W., Luo, M., Li, N.: A study of probabilistic password models. In: \n   915\tIEEE\n   916\t S&P 2014, pp. 538–552 (2014) \n   917\t11. Mainka, C., Mladenov, V., Schwenk, J., Wich, T.: Sok: single sign-on security — an \n   918\tev\n   919\taluation of OpenID connect. In: 2017 IEEE European Symposium on Security \n   920\tand Privacy (EuroS&P), pp. 251–266 (2017) \n   921\t12. Melicher, W., et al.: Fast, lean, and accurate: modeling password guessability using \n   922\tneural\n   923\t networks. In: USENIX Security 2016, pp. 175–191 (2016) \n   924\t13. Negi, P., Sharma, P., Jain, V., Bahmani, B.: K-means++ vs. behavioral biometrics: \n   925\tone\n   926\t loop to rule them all (2018) \n   927\t14. Nicholas, M.: 68 million reasons why your small business needs a password man-\n   928\tager.\n   929\t Dashlane Blog (2017). https://blog.dashlane.com/68-million-reasons-why-\n   930\tyour-small-business-needs-a-password-manager/ \n   931\t15. NordPass: How many passwords does the average person have? Average user holds \n   932\t168\n   933\t personal and 87 work passwords (2024) \n   934\t16. Pal, B., Daniel, T., Chatterjee, R., Ristenpart, T.: Beyond credential stuffing: \n   935\tpassw\n   936\tord similarity models using neural networks. In: 2019 IEEE Symposium on \n   937\tSecurity and Privacy (SP), pp. 417–434 (2019) \n   938\t17. Pasquini, D., Ateniese, G., Troncoso, C.: Universal neural-cracking-machines: self-\n   939\tconfigurable\n   940\t password models from auxiliary data. In: IEEE S&P 2024, pp. 1365– \n   941\t1384, Los Alamitos, CA, USA, May 2024. IEEE Computer Society (2024) \n   942\t18. Pearman, S., et al.: Let’s go in for a closer look: observing passwords in their natural \n   943\thabitat.\n   944\t In: Proceedings of the 2017 ACM SIGSAC Conference on Computer and \n   945\tCommunications Security, CCS ’17, pp. 295–310, New York, NY, USA. Association \n   946\tfor Computing Machinery (2017) \n   947\t19. Vaswani, A., et al.: Attention is all you need. In: NIPS 2017, vol. 30 (2017) \n   948\t20. Wang, D., Zou, Y., Xiao, Y.-A., Ma, S., Chen, X.: Pass2Edit: a multi-step genera-\n   949\ttiv\n   950\te model for guessing edited passwords. In: 32nd USENIX Security Symposium \n   951\t(USENIX Security 23), pp. 983–1000, Anaheim, CA, August 2023. USENIX Asso-\n   952\tciation (2023) \n   953\t21. Xiu, K., Wang, D.: PointerGuess: targeted password guessing model using pointer \n   954\tmechanism. In: 33rd USENIX Security Symposium (USENIX Security 24), pp. \n   955\t5555–5572, Philadelphia, PA, August 2024. USENIX Association (2024) ",
    "lineOffset": 600,
    "linesRead": 355,
    "totalLines": 955
  }

```
好的，我已经完整阅读了Pass2Pass-T的论文。现在来详细回答你的两个问题。

---

## 一、可以直接引用的精确数据 vs 需要从折线图提取的数据

### ✅ 可以直接引用的精确数据（表格中的）

**Table 2：Multi-Leak场景（6个子场景 × 6个guessnum）**

| Leak Num | Guess Num | FLA | Pass2Edit | Pass2Path | PointerGuess | Transformer | Pass2Pass-T |
|----------|-----------|-----|-----------|-----------|--------------|-------------|-------------|
| ≥1 | 1 | 2.59% | 43.51% | 43.51% | 46.26% | 47.03% | 47.23% |
| ≥1 | 5 | 2.98% | 55.65% | 55.23% | 56.32% | 57.41% | 57.61% |
| ≥1 | 10 | 3.68% | 56.95% | 56.29% | 57.47% | 58.68% | 58.91% |
| ≥1 | 100 | 5.94% | 60.29% | 58.22% | 60.72% | 61.88% | 62.00% |
| ≥1 | 1000 | 8.44% | 63.26% | 59.61% | 62.88% | 64.37% | 64.67% |
| ≥1 | 10^7 | 40.49% | \ | \ | 76.27% | 79.25% | 79.40% |
| ≥2 | 1 | 2.76% | 49.11% | 48.34% | 54.38% | 55.34% | 55.95% |
| ≥2 | 5 | 3.20% | 67.18% | 67.84% | 68.25% | 69.65% | 69.81% |
| ≥2 | 10 | 3.79% | 68.65% | 69.08% | 69.62% | 71.09% | 71.27% |
| ≥2 | 100 | 6.12% | 72.07% | 71.14% | 72.72% | 73.96% | 74.02% |
| ≥2 | 1000 | 8.76% | 74.94% | 72.40% | 74.81% | 76.02% | 76.18% |
| ≥2 | 10^7 | 41.30% | \ | \ | 83.65% | 85.95% | 86.43% |
| =5 | 1 | 3.25% | 45.03% | 45.13% | 57.02% | 58.50% | 59.70% |
| =5 | 5 | 4.11% | 74.60% | 76.98% | 76.02% | 78.58% | 78.89% |
| =5 | 10 | 4.76% | 77.00% | 78.90% | 78.21% | 80.63% | 80.84% |
| =5 | 100 | 7.12% | 80.81% | 81.09% | 81.87% | 83.17% | 83.29% |
| =5 | 1000 | 9.65% | 83.58% | 82.09% | 83.48% | 84.35% | 84.43% |
| =5 | 10^7 | 37.42% | \ | \ | 88.68% | 89.80% | 89.96% |
| ≥1(no repeat) | 1 | 2.17% | 0.73% | 0.61% | 1.00% | 1.08% | 1.27% |
| ≥1(no repeat) | 5 | 2.95% | 11.08% | 7.87% | 10.82% | 12.38% | 12.74% |
| ≥1(no repeat) | 10 | 3.16% | 13.12% | 9.88% | 12.99% | 15.01% | 15.34% |
| ≥1(no repeat) | 100 | 4.90% | 18.61% | 13.95% | 19.07% | 21.08% | 21.40% |
| ≥1(no repeat) | 1000 | 7.34% | 23.83% | 16.51% | 23.45% | 26.19% | 26.71% |
| ≥1(no repeat) | 10^7 | 36.94% | \ | \ | 49.89% | 56.99% | 56.84% |
| ≥2(no repeat) | 1 | 2.67% | 0.18% | 0.23% | 0.69% | 1.12% | 1.98% |
| ≥2(no repeat) | 5 | 3.18% | 10.92% | 7.27% | 9.76% | 12.75% | 13.48% |
| ≥2(no repeat) | 10 | 3.67% | 14.19% | 10.96% | 13.49% | 17.00% | 17.49% |
| ≥2(no repeat) | 100 | 5.89% | 21.82% | 16.71% | 22.07% | 24.93% | 25.39% |
| ≥2(no repeat) | 1000 | 8.47% | 27.90% | 20.52% | 27.16% | 30.54% | 31.21% |
| ≥2(no repeat) | 10^7 | 38.84% | \ | \ | 53.03% | 59.87% | 60.48% |
| =5(no repeat) | 1 | 2.93% | 0.18% | 0.24% | 0.67% | 2.02% | 4.87% |
| =5(no repeat) | 5 | 3.92% | 9.64% | 4.95% | 8.39% | 13.58% | 16.36% |
| =5(no repeat) | 10 | 4.28% | 15.84% | 12.38% | 13.57% | 21.02% | 21.99% |
| =5(no repeat) | 100 | 7.21% | 25.95% | 21.54% | 26.02% | 31.54% | 32.01% |
| =5(no repeat) | 1000 | 9.93% | 33.49% | 26.52% | 32.59% | 36.49% | 36.93% |
| =5(no repeat) | 10^7 | 39.44% | \ | \ | 53.35% | 58.70% | 59.33% |

**Table 5：消融实验（=5, no repeat）**

| Guess Num | Pass2Pass-T | Transformer+zip_pw | Transformer | Transformer_sspm | Pass2Edit |
|-----------|-------------|---------------------|-------------|------------------|-----------|
| 1 | 4.87% | 4.22% | 2.02% | 0.22% | 0.18% |
| 5 | 16.36% | 15.25% | 13.58% | 6.80% | 9.64% |
| 10 | 21.99% | 20.64% | 21.02% | 17.37% | 15.84% |
| 100 | 32.01% | 31.50% | 31.54% | 29.90% | 25.95% |
| 1000 | 36.93% | 36.72% | 36.49% | 35.53% | 33.49% |

**Table 6：Single-Leak场景**

| Setting | Guess Num | Pass2Edit | PointerGuess | Pass2Pass-T |
|---------|-----------|-----------|--------------|-------------|
| **A: Tianya→Dodonew(train); Tianya→Taobao(test)** | | | | |
| =1 | 1 | 27.28% | 27.73% | 26.94% |
| =1 | 5 | 31.10% | 31.10% | 31.24% |
| =1 | 10 | 32.15% | 31.99% | 32.26% |
| =1 | 100 | 34.09% | 34.20% | 34.33% |
| =1 | 1000 | 36.40% | 36.27% | 36.58% |
| =1 | 10^7 | – | 50.14% | 52.38% |
| **B: RMDC 7M(train); RMDC 100K(test)** | | | | |
| =1 | 1 | 40.42% | 40.21% | 40.64% |
| =1 | 5 | 46.88% | 47.05% | 48.05% |
| =1 | 10 | 48.19% | 47.92% | 49.23% |
| =1 | 100 | 51.13% | 51.45% | 52.41% |
| =1 | 1000 | 53.94% | 53.55% | 55.42% |

**Table 7：三种猜测策略对比（Appendix B）**
**Table 8：Monte Carlo vs Beam Search对比（Appendix C）**

这些表格数据都可以直接引用。

---

### 📊 需要从折线图提取的数据

论文中有以下折线图：

| 图号 | 内容 | X轴 | Y轴 | 包含的方法 |
|------|------|-----|------|-----------|
| **Fig.3** (a)(b)(c) | Repeat Multi-Leak场景，Top 1000 guesses内的攻击成功率 | Guess Number (1-1000) | Crack Rate | 所有方法 |
| **Fig.4** (a)(b)(c) | No-Repeat Multi-Leak场景，Top 1000 guesses内的攻击成功率 | Guess Number (1-1000) | Crack Rate | 所有方法 |
| **Fig.5** (a)(b)(c) | No-Repeat场景下与FLA的对比（高guess数） | Guess Number (大范围) | Crack Rate | FLA, Pass2Pass-T等 |

**关键点**：Table 2已经给出了guessnum = 1, 5, 10, 100, 1000, 10^7的精确数据。折线图（Fig.3和Fig.4）展示的是1到1000之间**连续的**曲线变化趋势。

### 你如何利用折线图数据？

**实际上你可能不需要提取折线图数据。** 原因如下：

1. **Table 2已经覆盖了所有关键对比点**（1, 5, 10, 100, 1000, 10^7），这些是学术论文中标准的对比点
2. 折线图主要是为了展示**趋势**，而不是精确数值
3. 你在自己的论文中，只需要在相同的guessnum点上对比即可

**如果你确实需要折线图中间点的数据**（比如guessnum=50, 200, 500等），用**WebPlotDigitizer**：
1. 截图Fig.3/Fig.4
2. 上传到 https://automeris.io/WebPlotDigitizer/
3. 标定坐标轴
4. 提取数据点
5. 论文中注明："Values at intermediate guess counts are extracted from figures in [Pass2Pass-T] using WebPlotDigitizer"

**我的建议**：直接用Table 2和Table 6的精确数据做对比就够了。如果你想画折线图展示趋势，就在相同的guessnum点（1, 5, 10, 100, 1000）上画你自己的线和他们的线。

---

## 二、Pass2Pass-T的叙事结构分析 + 你如何模仿

### Pass2Pass-T的论文结构拆解


总页数：约19页（LNCS格式，含附录）
正文约15页 + 附录约4页


#### Section 1: Introduction（约2.5页）

**叙事逻辑（四段式）**：


第1段：背景铺垫
  "密码仍然是最广泛使用的认证方式"
  → 用户管理255个密码（引用NordPass调查）
  → 因为记忆限制，用户复用密码
  → 所以密码容易被猜测攻击

第2段：问题升级——多次泄露是现实威胁
  → 引用2018年研究：平均每个账户3次泄露
  → 引用RMDC数据：690万用户至少5个密码泄露
  → 自己做了验证实验（Fig.1）：25%用户在5个以上域名泄露
  【关键技巧：用自己的小实验验证问题的真实性】

第3段：现有工作的不足
  → Das et al., Pass2Path, Pass2Edit, PointerGuess都只关注single-leak
  → MSPointerGuess虽然做了multi-leak，但有严重局限性
    （每个泄露密码需要独立encoder，不可扩展）
  【关键技巧：不是笼统说"别人没做"，而是具体指出技术局限】

第4段：Our Contributions（结构化列表）
  → 贡献1：提出Pass2Pass-T（技术贡献）
  → 贡献2：在multi-leak和single-leak都优于现有方法（实验贡献）
  → 贡献3：支持任意数量的泄露密码（实用性贡献）
  【关键技巧：贡献点用bullet list，每个都有量化数字】


**你可以模仿的写法**：

第1段：密码复用是普遍现象（和他一样）
第2段：现有targeted guessing方法的局限
  → Pass2Edit/Pass2Path/PointerGuess都是端到端生成密码
  → 不可解释，不能集成到现有工具链（HashCat）
  → 规则是password-independent的（HashCat Best64）
  【你的问题升级：缺少password-dependent的规则生成】
第3段：LLM的机会
  → LLM在序列生成任务上表现优异
  → 但直接用LLM做密码猜测是"杀鸡用牛刀"
  → 我们发现LLM特别适合做"规则生成"这个中间任务
第4段：Our Contributions
  → 贡献1：提出password-to-rule范式
  → 贡献2：基于LLM微调的规则生成模型
  → 贡献3：系统性评估（含Zero-shot/Few-shot对比）


---

#### Section 2: Related Work（约1页）

**结构**：

2.1 Password Reuse Behaviors（半页）
  → Florencio & Herley 2007（首次大规模研究）
  → Das et al. 2014（用网站数据验证）
  → Pearman et al. 2017（含特殊字符的密码更容易复用）
  【技巧：按时间线讲故事，每篇1-2句话】

2.2 Personalized Password Guessing via Leaked Passwords（半页）
  → Pass2Path 2019（seq2seq + 字符级编辑）
  → Pass2Edit 2023（多步分类，+43%）
  → PointerGuess 2024（指针网络，支持multi-leak）
  【技巧：每个工作都说了"做了什么"和"局限是什么"】


**你可以模仿的写法**：

2.1 Password Reuse and Transformation（和他类似）
2.2 Targeted Password Guessing（和他类似，加上PassLM 2025）
2.3 LLM for Security Tasks（新增，简短）
  → PassGPT, PassLM等
  → 说明LLM在密码领域的应用趋势


---

#### Section 3: Method（约3页）

**结构**：

3.1 Dataset Collection and Pre-Processing（1页）
  → 数据来源（RMDC）
  → 清洗步骤（3个过滤器）
  → 聚合策略（按email而非username）
  【技巧：数据处理写得非常详细，增加可复现性】

3.2 Password Reuse Behaviors（半页）
  → Table 1：8个典型案例
  → 分析两种复用模式：片段拼接、习惯性变换
  【技巧：用具体案例让reviewer直观理解问题】

3.3 Multi-password Model（1.5页）
  → Input Data Handling（3种策略的对比）
  → Segment-Wise Positional Encoding
  → Pre-training策略
  【技巧：每个设计决策都有对比和理由】

3.4 Monte-Carlo PPSM（半页）
  → 密码强度估计器


**你可以模仿的写法**：

3.1 Problem Formulation
  → 定义：给定旧密码p_old，生成Top-k条HashCat规则r1, r2, ..., rk
  → 每条规则ri应用到p_old上得到候选密码ci
  → 目标：最大化ci命中p_new的概率

3.2 Rule Extraction via A* Algorithm
  → 问题建模：从p_old到p_new的最短HashCat规则路径
  → A*算法细节
  → 多义性讨论（正面回应李教授的concern）
  → 数据清洗（去除位置相关规则、长规则、低频规则）

3.3 LLM Fine-tuning for Rule Generation
  → 基座模型选择（Qwen3-1.7B）
  → 字符级间隔化处理
  → DoRA微调策略
  → 训练细节

3.4 Decoding Strategies
  → Sampling
  → Beam Search
  → BFS
  → 三种策略的对比和适用场景


---

#### Section 4: Evaluation（约6页，最重要的部分）

**结构和叙事逻辑**：


4.1 Experimental Setting（1页）
  → 为什么选RMDC（批评MSPointerGuess的设置不现实）
  → 实验协议（follow Pass2Path的设置）
  → 6个场景的定义（≥1, ≥2, =5, 各有repeat/no-repeat）
  → 超参数设置
  → 训练细节（GPU、时间）
  【技巧：设置写得极其详细，让reviewer无法质疑实验公平性】

4.2 Ethical Considerations（半页）
  → 数据仅用于密码保护研究
  → 所有展示的密码都经过匿名化
  【技巧：安全领域必须有这一节】

4.3 Estimation for Crack Rate（半页）
  → Beam Search（≤1000 guesses）
  → Monte Carlo（高guess数）
  【技巧：明确说明评估方法，这是你也需要对齐的】

4.4 Multi-Leak Results（1.5页）
  → Table 2（核心结果表）
  → Fig.3, Fig.4（折线图）
  → 关键发现的文字描述
  【技巧：先给数据，再解读数据】

4.5 Result Analysis（1页）
  → Table 3：具体案例分析
  → 解释为什么multi-leak模型更好
  【技巧：用3个具体案例让reviewer直观理解】

4.6 High Guess Numbers（半页）
  → Fig.5 + Table 4
  → 反驳Pass2Path的结论

4.7 Ablation Study（半页）
  → Table 5
  → 逐个去除组件，验证每个的贡献

4.8 Single-Leak Evaluation（半页）
  → Table 6
  → Setting A和Setting B
  → 承认在single-leak下提升不大
  【技巧：诚实承认局限性，反而增加可信度】


**你可以模仿的写法**：

4.1 Experimental Setting
  → 数据集描述（你的6个泄露库 / RMDC如果拿到）
  → 训练/测试划分
  → 超参数
  → 对比方法列表

4.2 Ethical Considerations

4.3 Evaluation Metrics
  → Crack Rate @ k guesses的定义
  → 你的评估流程：旧密码→模型生成规则→应用规则→比对新密码

4.4 Main Results: Single-Leak Scenario
  → 核心对比表（你 vs PassLM vs Pass2Pass vs 统计Baseline vs HashCat Best64）
  → 折线图

4.5 Baseline Comparison: Zero-shot vs Few-shot vs Fine-tuning
  → 回应"Fine-tuning是否必要"的问题
  → 这是你的独特实验，Pass2Pass-T没有做

4.6 Analysis: Why Does LLM Improve Rule Ranking?
  → Diff Set分析
  → 概率排序价值分析
  → 具体案例展示

4.7 Cross-Site Transferability（如果做了跨站实验）

4.8 Ablation Study
  → 训练集大小、模型大小、A*规则质量等

4.9 Interpretability Analysis
  → Top-20高频规则统计
  → 典型案例展示


---

### Pass2Pass-T的关键文笔技巧（你应该模仿的）

#### 技巧1：用量化数字开场
> "compromises 4.87% of user accounts on the first guess, achieving a 7.27× improvement"

**不要写**："our method significantly outperforms..."
**要写**："our method cracks X% of accounts at the first guess, a Y× improvement over..."

#### 技巧2：承认局限性反而加分
> "We observe no significant performance difference, indicating that the previous approach is already sufficient to capture single-password modification patterns within 1,000 guesses."（Table 6的讨论）

他们在single-leak场景下承认自己没有显著优势，这反而让reviewer觉得诚实可信。

**你也应该这样做**：如果你在多步变换上不如别人，直接承认，然后解释原因。

#### 技巧3：批评前人工作要具体且技术化
> "MSPointerGuess encodes leaked passwords from each website using separate encoders that share only architecture but not parameters... this design implies a rigid model structure that must be specifically tailored or trained for each distinct number of leaked passwords"

**不要写**："previous methods have limitations"
**要写**：具体指出技术架构的哪个设计导致了什么问题

#### 技巧4：每个设计决策都有对比实验支撑
他们测试了3种Input Data Handling策略（BPE、Keyboard-mapping、Repetition-aware compression），最终选了第3种。这让reviewer觉得每个选择都是经过验证的，不是拍脑袋决定的。

**你也应该这样做**：比如你选择DoRA而不是LoRA，要有对比数据。

#### 技巧5：案例分析让论文生动
Table 3展示了3个具体案例，每个都详细解释了模型的推理过程。这比纯数字表格有说服力得多。

**你必须做**：展示5-10个案例，格式如下：

旧密码: password123
模型生成的Top-5规则: $4, sa@, $!, c, ]
对应的候选密码: password1234, p@ssword123, password123!, Password123, password12
真实新密码: p@ssword123 ✓（第2条规则命中）


---

### 你的论文和Pass2Pass-T的核心差异定位

| 维度 | Pass2Pass-T | 你的方法 |
|------|-------------|---------|
| **输入** | 多个泄露密码 | 单个泄露密码 |
| **输出** | 直接生成候选密码 | 生成HashCat规则 |
| **模型** | 从零训练的小Transformer（512维，8层） | 微调的LLM（Qwen3-1.7B） |
| **核心卖点** | Multi-leak场景 | 规则可解释性 + Password-dependent规则 |
| **评估** | Beam Search + Monte Carlo | Beam Search / Sampling / BFS |

**你不需要和他在multi-leak上竞争**。你的战场是：
1. **Single-leak场景**（Table 6是你的主要对比对象）
2. **规则的可解释性**（他完全没有）
3. **Zero-shot/Few-shot分析**（他完全没有）
4. **规则的概率排序价值**（他完全没有）

---

### 最终建议：你的论文模板


Title: Password-Dependent Rule Generation via Fine-tuned LLM 
       for Targeted Password Guessing

Abstract (200字)
1. Introduction (2.5页)
2. Related Work (1页)
3. Methodology (3页)
   3.1 Rule Extraction via A*
   3.2 LLM Fine-tuning
   3.3 Decoding Strategies
4. Evaluation (5-6页)
   4.1 Experimental Setting
   4.2 Ethical Considerations
   4.3 Main Results (对比表 + 折线图)
   4.4 Zero-shot vs Few-shot vs Fine-tuning
   4.5 Why LLM Improves Rule Ranking (Diff Set分析)
   4.6 Interpretability Analysis (案例 + 规则分布)
   4.7 Ablation Study
5. Discussion (1页)
   5.1 A* Multi-path Ambiguity
   5.2 Limitations of Character-level Rules
   5.3 Ethical Implications
6. Conclusion (0.5页)
References
Appendix: 详细的规则统计、更多案例


总页数控制在18页以内（LNCS格式，ACSAC/ESORICS的要求）。
```

**user**: 

```
那我感觉目前来看是不是只有Single-Leak场景中的RMDC 7M(train); RMDC 100K(test)数据我可以引用？其他的感觉都没啥引用价值啊
```

**assistant**: 

```


你说得很对，让我重新仔细审视一下哪些数据对你真正有用。

---

## 你的判断基本正确，但让我帮你再细想一下

### 你的实验设置 vs Pass2Pass-T的实验设置

先明确你的场景：
- **你做的是Single-Leak**（一个旧密码→预测新密码）
- **你的输出是规则**（不是直接生成密码）
- **你的数据来源是中文泄露库**（7k7k、Dodonew等）或者RMDC（如果拿到）

Pass2Pass-T的数据分布：

| 表格 | 场景 | 数据集 | 对你有用吗？ |
|------|------|--------|-------------|
| **Table 2** | Multi-Leak（≥1, ≥2, =5） | RMDC | ❌ 你不做multi-leak |
| **Table 5** | 消融实验（=5, no repeat） | RMDC | ❌ 他的消融，和你无关 |
| **Table 6 Setting A** | Single-Leak, Tianya→Dodonew(train); Tianya→Taobao(test) | 中文库 | ⚠️ 见下面分析 |
| **Table 6 Setting B** | Single-Leak, RMDC 7M(train); RMDC 100K(test) | RMDC | ✅ 最直接可引用 |
| **Table 7** | 猜测策略对比 | RMDC | ❌ 他的内部对比 |
| **Table 8** | Monte Carlo vs Beam Search | RMDC | ❌ 他的内部对比 |

---

### Table 6 Setting A 其实你也应该关注

Setting A的设置是：
> **训练集**：Tianya × Dodonew 的密码对
> **测试集**：Tianya × Taobao 的密码对

这个设置用的是**中文泄露库**，和你现在用的数据源（7k7k、Dodonew、17173等）是同一类数据。

**问题是**：你的数据集划分方式和他不完全一样。他是跨站点的（训练用Tianya×Dodonew，测试用Tianya×Taobao），你目前是同库内70/30划分。

但这恰恰给了你两个选择：

**选择1：复现他的Setting A**
如果你手上有Tianya、Dodonew、Taobao这三个库（你之前提到你有Dodonew），你可以：
- 用完全相同的训练/测试划分
- 直接引用他Table 6 Setting A的数字作为baseline
- 这样对比最公平，reviewer无法质疑

**选择2：只用Setting B（RMDC）**
如果你拿到了RMDC数据，直接对齐Setting B。

---

### 但是，有一个更深层的问题

即使你引用了Table 6的数字，**对比仍然不完全公平**，因为：

| 维度 | Pass2Pass-T | 你的方法 |
|------|-------------|---------|
| 输出 | 直接生成候选密码 | 生成规则→应用规则→得到候选密码 |
| 评估 | Beam Search生成Top-k候选密码 | 你的解码策略生成Top-k规则→Top-k候选密码 |
| 模型 | 从零训练的小Transformer | 微调的LLM |

**输出形式不同**意味着：
- 他的1次guess = 1个候选密码
- 你的1次guess = 1条规则 → 1个候选密码

这两者在guess number的计算上是对齐的（都是1条规则/1个密码 = 1次guess），所以**Crack Rate @ k guesses是可以直接对比的**。

---

### 实际可引用的数据汇总

**最有价值的引用数据（Table 6 Setting B）**：

| Guess Num | Pass2Edit | PointerGuess | Pass2Pass-T |
|-----------|-----------|--------------|-------------|
| 1 | 40.42% | 40.21% | 40.64% |
| 5 | 46.88% | 47.05% | 48.05% |
| 10 | 48.19% | 47.92% | 49.23% |
| 100 | 51.13% | 51.45% | 52.41% |
| 1000 | 53.94% | 53.55% | 55.42% |

**次有价值的引用数据（Table 6 Setting A）**：

| Guess Num | Pass2Edit | PointerGuess | Pass2Pass-T |
|-----------|-----------|--------------|-------------|
| 1 | 27.28% | 27.73% | 26.94% |
| 5 | 31.10% | 31.10% | 31.24% |
| 10 | 32.15% | 31.99% | 32.26% |
| 100 | 34.09% | 34.20% | 34.33% |
| 1000 | 36.40% | 36.27% | 36.58% |
| 10^7 | – | 50.14% | 52.38% |

---

### 你现在面临的核心决策

**情况A：你拿到了RMDC数据**
→ 直接对齐Table 6 Setting B，引用他的数字，在相同数据上跑你的方法
→ 这是最理想的情况

**情况B：你拿不到RMDC数据**
→ 你有两条路：

**路线B-1：复现Setting A（推荐）**
- 你需要Tianya、Dodonew、Taobao三个库
- 用他完全相同的划分方式
- 直接引用Table 6 Setting A的数字
- **你手上有这三个库吗？**

**路线B-2：用你自己的数据集，不直接引用他的数字**
- 在你自己的数据集上跑PassLM（有开源代码）
- 在你自己的数据集上跑你的方法
- 不引用Pass2Pass-T的数字（因为数据集不同，不可比）
- Pass2Pass-T只在Related Work中讨论，不做数值对比
- **这条路的好处是不需要RMDC，不需要对齐他的设置**

---

### 我的建议

**优先级排序**：

1. **最优**：拿到RMDC → 对齐Setting B → 直接引用Table 6 Setting B
2. **次优**：用Tianya+Dodonew+Taobao → 对齐Setting A → 直接引用Table 6 Setting A
3. **保底**：用你自己的数据集 → 跑PassLM作为baseline → 不引用Pass2Pass-T的具体数字

无论哪条路，**PassLM（有开源代码）都应该是你的主要对比对象**，因为：
- 它是2025年最新的
- 有代码可以在任何数据集上跑
- 是王鼎组的最新工作，比Pass2Pass-T更新
- 不依赖于特定数据集

**所以你现在最紧迫的事情是**：
1. 确认RMDC数据申请的进展
2. 确认你手上有没有Tianya和Taobao
3. 开始跑PassLM的代码

你手上目前有哪些库？Tianya和Taobao有吗？
```



--------------------


<a href="https://chatboxai.app" style="display: flex; align-items: center;">
<img src='https://chatboxai.app/icon.png' style='width: 40px; height: 40px; padding-right: 6px'>
<b style='font-size:30px'>Chatbox AI</b>
</a>
