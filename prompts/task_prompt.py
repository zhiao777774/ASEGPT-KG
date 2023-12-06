RELATION_EXTRACTION_PROMPT = '''
    給定一段新聞段落，請幫我從中找出所有的知識圖譜三元組 (頭實體, 關係, 尾實體)。請幫我過濾掉對於構成新聞段落不重要的三元組，並只給我過濾後的結果。 注意：新聞段落內可能有一個以上的三元組存在，若有多個三元組，格式請以[(頭實體1, 關係1, 尾實體1), (頭實體2, 關係2, 尾實體2)]以此類推呈現。
    {DEMONSTRATION}
    <新聞段落>
    {INPUT}
    <答案>
'''

UNFILTERED_RELATION_EXTRACTION_PROMPT = '''
    給定一段新聞段落，請幫我從中找出所有的知識圖譜三元組 (頭實體, 關係, 尾實體)，如果有你覺得有缺失的關係，請把它補上。 注意：新聞段落內可能有一個以上的三元組存在，若有多個三元組，格式請以[(頭實體1, 關係1, 尾實體1), (頭實體2, 關係2, 尾實體2)]以此類推呈現。
    {DEMONSTRATION}
    <新聞段落>
    {INPUT}
    <答案>
'''

RELATION_EXTRACTION_WITH_RATIONALE_PROMPT = '''
    你將執行關係抽取(Relation Extraction)任務。你將識別內容中的命名實體，然後提取它們之間的關係。
    讓我們一步一步思考，根據我提供的新聞段落，你將傳回格式為"命名實體 A, 關係, 命名實體 B"的三元組(Triplet)，與三元組對應的解釋(Rationale)。
    請多注意新聞段落中的量詞（例如：12%）及代名詞等（例如：他），這些應為組成新聞的重要資訊。
    首先給你一個範例，幫助你理解任務：
    {DEMONSTRATION}
    接著給你要做的新聞段落：
    <新聞段落>
    {INPUT}
    <答案>
'''

TRIPLETS_EXPLANATION_LABELING_PROMPT = '''
    給定一段新聞段落，以及你先前從段落中找到的多個經篩選後的重要知識圖譜三元組 (頭實體, 關係, 尾實體)。讓我們一步一步思考，請從新聞段落中找出理由，說明為什麼你認為這個三元組是正確的，或者應該被標註出來。請直接給我理由的文本就好。
    新聞段落：
    （蘋果（Apple）新款\n15 系列新機開放預購，不過已有科技網紅及測試機構拿到實體新機並測試\nPro 系列搭載的最新 A17 Pro 晶片，但卻掀起新款晶片功耗續航力論戰，也連帶讓法人關注臺積電3奈米家族話題。\n依據測試數據，蘋果宣傳業界首顆採用3奈米製程的手機 SoC，運作效能確實較一代提升，效能確實如\n上提供的數字一致，但功耗的部分也是衝上了新高點，這樣的表現讓不少人確實都感到失望，若和蘋果自身手機比較，目前續航力最佳的機種為 iPhone 15 Plus 但採用前一代 A16 晶片。至於 iPhone 15 Pro Max 功耗則比iPhone 14 Pro Max 來得高，引發市場討論問題所在。\n法人分析，根據蘋果首周的銷售數字大致持平去年的水準，蘋果並未有做任何加單的動作，並指出以這次 A17 PRO 版本來看可能並不是太成熟的版本，明年度蘋果將採用更便宜 的 n3E 的製程，推測該因素也是臺積電放緩資本支出的主要原因。\n99\nend of articles
    知識圖譜三元組：
    [(Pro 系列,搭載, A17 Pro 晶片), (法人, 關注, 臺積電3奈米), (蘋果, 宣傳,業界首顆採用3奈米製程的手機 SoC), (蘋果, 宣傳,運作效能確實較一代提升), (續航力最佳的機種, 為, iPhone 15 Plus), (續航力最佳的機種, 採用, 前一代 A16 晶片), (法人, 分析, 蘋果首周的銷售數字大致持平去年的水準), (法人, 分析, 蘋果並未有做任何加單的動作), (法人, 指出, 這次 A17 PRO 版本來看可能並不是太成熟的版本，明年度蘋果將採用更便宜 的 n3E 的製程), (法人, 推測, 臺積電放緩資本支出的主要原因)]
    解釋：
    (Pro 系列,搭載, A17 Pro 晶片)：新聞段落明確提到“Pro 系列搭載的最新 A17 Pro 晶片”，這個三元組直接反映了新聞的內容，因此是正確的。
    (法人, 關注, 臺積電3奈米)：文中提到了“也連帶讓法人關注臺積電3奈米家族話題”，這表明法人對於臺積電的3奈米技術有所關注，因此這個三元組也是正確的。
    (蘋果, 宣傳,業界首顆採用3奈米製程的手機 SoC)：文本中的“蘋果宣傳業界首顆採用3奈米製程的手機 SoC”直接對應了這個三元組，所以它是正確的。
    (蘋果, 宣傳,運作效能確實較一代提升)：新聞中明言“運作效能確實較一代提升”，且是蘋果的宣傳，因此這個三元組是正確的。
    (續航力最佳的機種, 為, iPhone 15 Plus)：新聞中有“目前續航力最佳的機種為 iPhone 15 Plus”的文字，因此這個三元組是正確的。
    (續航力最佳的機種, 採用, 前一代 A16 晶片)：這段的“但採用前一代 A16 晶片”說明了續航力最佳的機種採用的是前一代 A16 晶片，所以這個三元組是正確的。
    (法人, 分析, 蘋果首周的銷售數字大致持平去年的水準)：文中的“法人分析，根據蘋果首周的銷售數字大致持平去年的水準”直接反映了這個三元組，所以它是正確的。
    (法人, 分析, 蘋果並未有做任何加單的動作)：這一句“蘋果並未有做任何加單的動作”也是法人的分析，因此這個三元組是正確的。
    (法人, 指出, 這次 A17 PRO 版本來看可能並不是太成熟的版本，明年度蘋果將採用更便宜 的 n3E 的製程)：文中的“法人指出以這次 A17 PRO 版本來看可能並不是太成熟的版本，明年度蘋果將採用更便宜 的 n3E 的製程”直接對應了這個三元組，所以它是正確的。
    (法人, 推測, 臺積電放緩資本支出的主要原因)：新聞段落中的“推測該因素也是積電放緩資本支出的主要原因”文字，展示了法人對於臺積電放緩資本支出的推測，因此這個三元組是正確的。
    新聞段落：
    {INPUT}
    知識圖譜三元組：
    {TRIPLETS}
    解釋：
'''
