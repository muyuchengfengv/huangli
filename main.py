from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger, AstrBotConfig

from astrbot.api import logger

@register("helloworld", "YourName", "一个简单的 Hello World 插件", "1.0.0")
class MyPlugin(Star):
    def __init__(self, context: Context,config: AstrBotConfig):
        super().__init__(context,config)
        self.api_key = config.get("DEEPSEEK_API_KEY", 100000)
        self.api_url = "https://api.deepseek.com/
        self.session = None

    async def initialize(self):
        """初始化异步HTTP会话"""
        self.session = aiohttp.ClientSession()
        logger.info("黄历插件已初始化，DeepSeek API 准备就绪")
    
    # 注册指令的装饰器。指令名为 helloworld。注册成功后，发送 `/helloworld` 就会触发这个指令，并回复 `你好, {user_name}!`
    @filter.command("每日黄历")
    async def helloworld(self, event: AstrMessageEvent):
        """这是一个查看每日黄历的方法""" # 这是 handler 的描述，将会被解析方便用户了解插件内容。建议填写。
        try:
                    # 1. 构造专业提示词
            today = datetime.now().strftime("%Y年%m月%d日")
            system_prompt = (
                "你是一位精通中国传统历法的玄学大师，请严格按照以下要求生成今日黄历：\n"
                "1. 包含公历日期、农历日期、干支纪年\n"
                "2. 详细列出宜/忌事项（至少各5项）\n"
                "3. 财神方位需精确到具体方向（如东北方）\n"
                "4. 包含冲煞生肖、吉神方位、胎神占位\n"
                "5. 使用传统术语但解释清晰\n"
                "6. 输出格式：使用emoji图标分段，每段开头用【】标注类别"
            )
            user_prompt = f"今天是{today}，请生成专业级的黄历内容"

            # 2. 调用DeepSeek API
            headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 1000
            }

            async with self.session.post(self.api_url, headers=headers, json=payload) as response:
                if response.status != 200:
                    error = await response.text()
                    logger.error(f"DeepSeek API 错误: {error}")
                    yield event.plain_result("黄历获取失败，请稍后再试")
                    return

                data = await response.json()
                huangli_content = data["choices"][0]["message"]["content"]

            # 3. 格式化输出
            formatted_output = (
                "✨ 今日专业黄历 ✨\n"
                "------------------\n"
                f"{huangli_content}\n"
                "------------------\n"
                "数据来源：DeepSeek玄学模型"
            )
            yield event.plain_result(formatted_output)

        except Exception as e:
            logger.exception("黄历生成异常")
            yield event.plain_result(f"黄历生成失败: {str(e)}")

    async def terminate(self):
        """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""
