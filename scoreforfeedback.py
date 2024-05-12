from data_pre import Storename

def score_for_feedback(feedbacks,a,b,c):
    total_score = 100  # 初始满分
    min_words = 8  # 最小字数要求
    penalty_per_feedback = 20  # 每个不达标输入的扣分
    feedbacks_to_check_stores = [1, 2, 4]

    for index, feedback in enumerate(feedbacks):
        # 检查是否为空或非常短的响应
        if len(feedback) < min_words:
            total_score -= penalty_per_feedback
            continue

        # 检查是否有具体细节
        if index in feedbacks_to_check_stores:
            if  (index == 1 and a != "均无") or (index == 2 and b != "均无") or (index == 4 and c != "均无"):
                if not any(store_name in feedback for store_name in Storename):  # 如果没有提及任何一个店铺名
                    total_score -= 10  # 未提及店铺名则再扣10分
                    print(f"Feedback penalty for not mentioning any store names: {feedback}")

        # 可以添加更多的检查，比如是否包含关键词等

    # 确保总分不低于0
    total_score = max(total_score, 0)

    # 将百分制分数标准化到 -5 到 +5 的区间
    normalized_score = (total_score - 50) * 0.1
    return normalized_score

# feedbacks_low = [
#     "模型A还行，但我不记得路线了",                 # 无具体店铺提及，缺少细节
#     "模型B的推荐让我走了很多路，感觉很累",           # 未明确提及绕路的具体行程段，缺少店铺名称
#     "我觉得都一样，没什么区别",                     # 缺乏具体理由，未提及具体模型和店铺
#     "A模型的行程太长了",                            # 未提到具体的耗时店铺，缺少具体信息
#     "B模型推荐的店铺太重复了"                        # 未列举具体重复的店铺名
# ]
feedbacks_high = [
    "模型A推荐了'ZARA', 'Nike Kicks Lounge' 和 'GUESS'，非常符合我的购物兴趣，既有服装也有运动鞋", # 具体提及符合兴趣的店铺名
    "模型B的路径从'SEPHORA'到'星巴克'再到'Nike Kicks Lounge', 行程连贯而且没有多余的走动，非常便利", # 明确指出无绕路的行程段，具体店铺提及
    "考虑到时间限制，模型A推荐的店铺'小米之家'与'Miss Sixty'距离较近，可以节省大量时间", # 提及具体的时间节省店铺
    "模型B推荐的行程包含了服装店'GUESS', 鞋店'FILA'以及饮品店'喜茶'，确保了行程的多样性", # 指出行程多样性并列出具体店铺名
    "模型A多次推荐了服装店，包括'ZARA', 'Tommy Hilfiger'和'Armani Exchange'，这超出我的需求并让我感到有些乏味", # 指出重复推荐和具体店铺名
]
a = "均无"
b = "模型A"
c = "均无"
# final_score = score_for_feedback(feedbacks_low)
# print("Your feedback score adjusted reward: ", final_score)
final_score = score_for_feedback(feedbacks_high,a,b,c)
print("Your feedback score adjusted reward: ", final_score)
