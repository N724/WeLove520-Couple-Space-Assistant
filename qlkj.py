# -*- coding: utf-8 -*-
import requests
import time
import random
from datetime import datetime, timezone, timedelta, date
import logging
import sys
from typing import Dict, List, Optional, Tuple, Any
import calendar # Needed for Gregorian leap year check

# ====================== 配置区 ======================
ACCOUNTS = [
    {
        "name": "我们的小窝❤",
        "access_token": "",
        "lover_name": "霞宝宝❤",
    },
    {
       "name": "我们的小窝❤",
       "access_token": "",
       "lover_name":"小汪❤",
    }
]

# --- 生日日期覆盖配置 ---
# *** 重要 ***
# 键(Key): 必须与你在 WeLove App 中设置的生日描述 *完全一致* 才能生效!
#          例如，如果App里的描述是 "小汪汪的生日"，这里就必须写 "小汪汪的生日"
# 值(Value): 目标日期，格式 "YYYY-MM-DD"
BIRTHDAY_OVERRIDES = {
    # --- 请根据你 App 中的实际描述修改下面的 Key ---
    "冰镇西瓜汁汁汁汁的生日": "2025-09-15",  # <--- 修改这里的 Key
    "ᓚᘏᗢ的生日": "2025-12-14",  # <--- 修改这里的 Key
    # --- 示例结束 ---
    # "其他需要覆盖的生日描述": "YYYY-MM-DD",
}
# -----------------------------

# WxPusher 配置
WXPUSHER_APP_TOKEN = "" # 替换成你的 WxPusher AppToken
WXPUSHER_UIDS = [""] # 替换成你的 WxPusher UID 列表

# 报告和任务设置
REPORT_SETTINGS = {
    "max_anniversaries": 5,
    "timezone_offset": 8,
    "tree_fertilize_enabled": True,
    "tree_fertilize_attempts": 3,
    "tree_fertilize_delay": 10,
    "tree_watch_ads": True,
    "random_delay_min": 1.5,
    "random_delay_max": 3.5
}

# ====================== 常量定义 ======================
HEADERS_MAIN = {
    "Host": "mp.welove520.com", "Content-Type": "application/x-www-form-urlencoded",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.49(0x18003133) NetType/WIFI Language/zh_CN",
    "Referer": "https://servicewechat.com/wxdbee9b9d855d6263/468/page-frame.html",
    "Wxmp-Ua": "[brand:iPhone][model:iPhone 14 Pro Max][os:iOS][osv:17.5][weixin:8.0.49][scene:1001][network:wifi]"
}
HEADERS_TREE = {
    "Host": "tree.welove520.com", "Connection": "keep-alive", "CV": "5.19",
    "content-type": "application/x-www-form-urlencoded", "Accept-Encoding": "gzip,compress,br,deflate",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.49(0x18003133) NetType/WIFI Language/zh_CN",
    "Referer": "https://servicewechat.com/wxdbee9b9d855d6263/468/page-frame.html"
}
EMOJI_MAP = {
    "success": "✅", "failure": "❌", "warning": "⚠️", "info": "ℹ️", "duplicate": "💕", "heart": "❤️",
    "love": "💖", "couple": "👫", "stats": "📊", "calendar": "📅", "clock": "⏳", "birthday": "🎂",
    "anni": "🗓️", "punch": "💘", "missed": "🕳️", "tree": "🌳", "water": "💧", "sun": "☀️",
    "fertilizer": "🌱", "gift": "🎁", "ad": "📺", "level": "⭐", "growth": "📈", "check": "✔️",
    "cross": "❌", "loading": "🔄", "done": "👍", "rocket": "🚀", "skipped": "⏭️", "disabled": "🚫",
    "partial": "📊", "override": "🎯"
}

# 获取当前时区的 helper
def get_current_datetime() -> datetime:
    tz = timezone(timedelta(hours=REPORT_SETTINGS["timezone_offset"]))
    return datetime.now(tz)

# ====================== 日志配置 ======================
log_filename = 'welove520_integrated.log'
logger = logging.getLogger()
logger.setLevel(logging.INFO)
for handler in logger.handlers[:]: logger.removeHandler(handler)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(message)s')
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)
file_handler = logging.FileHandler(log_filename, mode='a', encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

# ====================== 网络请求封装 ======================
def make_request(url: str, method: str = "GET", headers: Optional[Dict] = None, data: Optional[Dict] = None, params: Optional[Dict] = None, is_json: bool = False, timeout: int = 15) -> Optional[Dict]:
    effective_headers = headers.copy() if headers else {}
    if is_json and method.upper() == "POST": effective_headers['Content-Type'] = 'application/json;charset=utf-8'
    try:
        delay = random.uniform(REPORT_SETTINGS["random_delay_min"], REPORT_SETTINGS["random_delay_max"])
        logging.debug(f"等待 {delay:.2f} 秒...")
        time.sleep(delay)
        session = requests.Session()
        request_args = {"headers": effective_headers, "timeout": timeout}
        if params: request_args["params"] = params
        logging.debug(f"发起请求: {method} {url}")
        if data: logging.debug(f"Data/Payload: {data}")
        if method.upper() == "GET": response = session.get(url, **request_args)
        elif method.upper() == "POST":
            if is_json: request_args["json"] = data
            else: request_args["data"] = data
            response = session.post(url, **request_args)
        else: logging.error(f"不支持的请求方法: {method}"); return None
        logging.debug(f"响应状态码: {response.status_code}")
        response.raise_for_status()
        response_json = response.json()
        logging.debug(f"响应 JSON: {response_json}")
        return response_json
    except requests.exceptions.Timeout: logging.error(f"请求超时: {url}")
    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTP 错误 ({url}): {e.response.status_code} {e.response.reason}")
        try: logging.error(f"响应内容: {e.response.text}")
        except Exception: pass
    except requests.exceptions.RequestException as e: logging.error(f"请求错误 ({url}): {e}")
    except Exception as e: logging.error(f"处理请求时发生未知错误 ({url}): {e}", exc_info=True)
    return None

# ====================== 核心功能模块 - 主应用 ======================
class Love520API:
    BASE_URL = "https://mp.welove520.com/v1/mp"

    @staticmethod
    def get_user_info(access_token: str) -> Optional[Dict]:
        url = f"{Love520API.BASE_URL}/my/info"; params = {"access_token": access_token}
        data = make_request(url, method="GET", headers=HEADERS_MAIN, params=params)
        if data and data.get("result") == 1: return data
        logging.warning(f"获取用户信息失败: {data}"); return None

    @staticmethod
    def daily_punch(access_token: str) -> Dict[str, Any]:
        url = f"{Love520API.BASE_URL}/daily/miss"; req_data = {"form_id": "0", "access_token": access_token}
        result = make_request(url, method="POST", headers=HEADERS_MAIN, data=req_data)
        if result:
            if result.get("result") == 1: return {"status": "success", "code": 1, "message": "想念宝宝成功"}
            elif result.get("result") == 2205: return {"status": "duplicate", "code": 2205, "message": "今天已经想过宝宝啦"}
            else: logging.warning(f"打卡异常响应: {result}"); return {"status": "error", "code": result.get("result"), "message": f"打卡失败: {result.get('error_msg', '未知错误')}"}
        return {"status": "network_error", "code": -1, "message": "打卡请求失败"}

    @staticmethod
    def get_punch_stats(access_token: str) -> Optional[Dict]:
        url = f"{Love520API.BASE_URL}/daily/miss/record"; now = get_current_datetime()
        req_data = {"begin_year": now.year, "begin_month": now.month, "access_token": access_token}
        data = make_request(url, method="POST", headers=HEADERS_MAIN, data=req_data)
        if data and data.get("result") == 1 and data.get("rows"):
            try:
                punch_data_str = data["rows"][0]["punchData"]
                return Love520API._analyze_punch_data(punch_data_str) # Use updated function
            except (IndexError, KeyError, TypeError) as e: logging.error(f"解析打卡统计数据错误: {e} | 原始数据: {data}"); return None
        logging.warning(f"获取打卡统计失败: {data}"); return None

    # *** 修改这里：计算月初开始的连签 ***
    @staticmethod
    def _analyze_punch_data(punch_data_str: str) -> Optional[Dict]:
        """分析打卡数据，计算月初开始的连签天数"""
        try:
            today_day = get_current_datetime().day
            valid_data = punch_data_str[:today_day]; punched_count = valid_data.count('1'); total_days = len(valid_data)

            # --- 计算月初开始的连签天数 ---
            initial_streak = 0
            for char in valid_data: # 从头开始遍历
                if char == '1':
                    initial_streak += 1
                else:
                    break # 遇到非 '1'，月初连签中断
            # ---------------------------------

            logging.debug(f"打卡分析: valid_data='{valid_data}', len={total_days}, punched={punched_count}, initial_streak={initial_streak}")
            calendar_viz = "".join([EMOJI_MAP["punch"] if day == '1' else EMOJI_MAP["missed"] for day in valid_data])
            return {"total_days": total_days, "punched_days": punched_count,
                    "initial_streak": initial_streak, # 使用新的字段名
                    "calendar_viz": calendar_viz, "completion_rate": round(punched_count / total_days * 100, 1) if total_days > 0 else 0}
        except Exception as e: logging.error(f"分析打卡数据时出错: {e} | 输入: {punch_data_str}"); return None

    @staticmethod
    def get_anniversaries(access_token: str) -> Optional[List[Dict]]:
        url = f"{Love520API.BASE_URL}/anni/list"; req_data = {"access_token": access_token}
        result = make_request(url, method="POST", headers=HEADERS_MAIN, data=req_data)
        if result and result.get("result") == 1:
            return Love520API._process_anni_data_no_lunar(result.get("annis", []))
        logging.warning(f"获取纪念日数据异常: {result}"); return None

    @staticmethod
    def _process_anni_data_no_lunar(annis_raw: List) -> List[Dict]:
        valid_annis = []; today_dt = get_current_datetime(); today_date = today_dt.date(); today_year = today_dt.year
        for item in annis_raw:
            if item.get("result") != 1: continue
            anni_detail = item.get("anni", {}); desc = anni_detail.get("desc", "无标题")
            try:
                g_year = anni_detail.get("year", 0); g_month = anni_detail.get("month", 0); g_day = anni_detail.get("day", 0)
                is_birthday_api_flag = anni_detail.get("date_type") == 1; is_repeat_api_flag = anni_detail.get("repeat_type", 0) == 1
                if g_year <= 0 or not (1 <= g_month <= 12) or not (1 <= g_day <= 31):
                    logging.warning(f"跳过纪念日 '{desc}': API返回无效日期组件 (Y={g_year}, M={g_month}, D={g_day})"); continue
                original_gregorian_date = date(g_year, g_month, g_day); days_passed = (today_date - original_gregorian_date).days
                next_event_date = None; days_left = None; is_override = False
                if is_birthday_api_flag:
                    override_date_str = BIRTHDAY_OVERRIDES.get(desc) # 使用 desc 从 API 获取的值进行查找
                    if override_date_str:
                        try:
                            target_date = datetime.strptime(override_date_str, "%Y-%m-%d").date()
                            if target_date >= today_date:
                                next_event_date = target_date; days_left = (next_event_date - today_date).days; is_override = True
                                logging.info(f"生日 '{desc}' 使用覆盖日期: {next_event_date}")
                            else: logging.warning(f"生日 '{desc}' 的覆盖日期 {override_date_str} 已过，将按已过处理。")
                        except ValueError: logging.error(f"生日 '{desc}' 的覆盖日期格式错误: '{override_date_str}'，应为 YYYY-MM-DD。将使用标准公历计算。")
                    if not is_override and not (override_date_str and next_event_date is None):
                        try:
                            this_year_date = original_gregorian_date.replace(year=today_year)
                            if this_year_date >= today_date: next_event_date = this_year_date
                            else: next_event_date = original_gregorian_date.replace(year=today_year + 1)
                        except ValueError:
                            if original_gregorian_date.month == 2 and original_gregorian_date.day == 29:
                                target_y = today_year
                                try:
                                    if date(today_year, 2, 29) < today_date: target_y += 1
                                except ValueError: target_y += 1
                                while True:
                                    if calendar.isleap(target_y): next_event_date = date(target_y, 2, 29); break
                                    target_y += 1;
                                    if target_y > today_year + 8: logging.error(f"计算公历闰年日期 '{desc}' 超出范围"); break
                            else: logging.warning(f"公历生日日期替换错误: {desc} - {original_gregorian_date}"); continue
                        if next_event_date and not is_override: logging.debug(f"计算出的下一个公历生日日期: {next_event_date}")
                elif is_repeat_api_flag:
                     if days_passed < 0: next_event_date = original_gregorian_date
                     else:
                         try:
                             this_year_date = original_gregorian_date.replace(year=today_year)
                             if this_year_date >= today_date: next_event_date = this_year_date
                             else: next_event_date = original_gregorian_date.replace(year=today_year + 1)
                         except ValueError:
                              if original_gregorian_date.month == 2 and original_gregorian_date.day == 29:
                                  target_y = today_year
                                  try:
                                      if date(today_year, 2, 29) < today_date: target_y += 1
                                  except ValueError: target_y += 1
                                  while True:
                                      if calendar.isleap(target_y): next_event_date = date(target_y, 2, 29); break
                                      target_y += 1;
                                      if target_y > today_year + 8: logging.error(f"计算公历闰年日期 '{desc}' 超出范围"); break
                              else: logging.warning(f"公历纪念日日期替换错误: {desc} - {original_gregorian_date}"); continue
                     if next_event_date: logging.debug(f"计算出的下一个重复纪念日日期: {next_event_date}")
                if next_event_date and days_left is None: # Recalculate days_left if needed (e.g., non-override birthday)
                     days_left = (next_event_date - today_date).days
                valid_annis.append({
                    "desc": desc, "date": f"{original_gregorian_date.year}-{original_gregorian_date.month:02d}-{original_gregorian_date.day:02d}",
                    "type": "birthday" if is_birthday_api_flag else "anni", "days_passed": max(days_passed, 0),
                    "days_left": days_left, "is_override": is_override,
                    "next_event_date_debug": str(next_event_date) if next_event_date else "None"
                })
            except (KeyError, ValueError, TypeError) as e: logging.warning(f"处理纪念日条目 '{desc}' 时遇到错误: {e}", exc_info=True); continue
        valid_annis.sort(key=lambda x: x["days_left"] if x["days_left"] is not None and x["days_left"] >= 0 else float('inf'))
        return valid_annis

# ====================== 核心功能模块 - 爱情树 ======================
# ... LoveTreeAPI 类保持不变 ...
class LoveTreeAPI:
    BASE_URL = "https://tree.welove520.com"
    @staticmethod
    def _request_tree(endpoint: str, access_token: str, data: Optional[Dict] = None) -> Dict:
        url = f"{LoveTreeAPI.BASE_URL}{endpoint}"; req_data = {"access_token": access_token};
        if data: req_data.update(data)
        if endpoint in ["/v1/game/tree/op", "/v2/game/tree/ad/view"] and "client_time" not in req_data: req_data["client_time"] = int(time.time())
        response = make_request(url, method="POST", headers=HEADERS_TREE, data=req_data)
        if not response: return {"status": "network_error", "message": "网络请求失败"}
        result_code = response.get("result"); error_msg = response.get("error_msg", "未知错误")
        if result_code == 1: return {"status": "success", "data": response}
        elif result_code in [1001, 1002, 1018]: return {"status": "already_done", "code": result_code, "message": error_msg}
        elif result_code == 1027: return {"status": "ad_limit", "code": result_code, "message": error_msg}
        elif result_code == 1003: return {"status": "condition_not_met", "code": result_code, "message": error_msg}
        elif result_code == 1029: return {"status": "condition_not_met", "code": result_code, "message": error_msg}
        else: logging.warning(f"树API请求返回错误: code={result_code}, msg='{error_msg}', endpoint={endpoint}, op/action={req_data.get('op') or req_data.get('action')}"); return {"status": "error", "code": result_code, "message": error_msg}
    @staticmethod
    def daily_water(access_token: str) -> Dict:
        token_short = access_token[:6]; logging.info(f"[{token_short}] 尝试浇水...")
        res = LoveTreeAPI._request_tree("/v1/game/tree/op", access_token, {"op": 1})
        if res["status"] == "success": res["message"] = f"浇水成功, 成长值 +{res['data'].get('growth_increase', 0)}"; logging.info(f"[{token_short}] {res['message']}")
        elif res["status"] != "network_error": logging.info(f"[{token_short}] 浇水结果: {res['message']}")
        return res
    @staticmethod
    def daily_sun(access_token: str) -> Dict:
        token_short = access_token[:6]; logging.info(f"[{token_short}] 尝试晒太阳...")
        res = LoveTreeAPI._request_tree("/v1/game/tree/op", access_token, {"op": 2})
        if res["status"] == "success": growth = res['data'].get('growth_increase', 0) or res['data'].get('extra_growth', 0); res["message"] = f"晒太阳成功, 额外成长值 +{growth}"; logging.info(f"[{token_short}] {res['message']}")
        elif res["status"] != "network_error": logging.info(f"[{token_short}] 晒太阳结果: {res['message']}")
        return res
    @staticmethod
    def fertilize(access_token: str) -> Dict:
        token_short = access_token[:6]; logging.info(f"[{token_short}] 尝试施肥 (单次)...")
        res = LoveTreeAPI._request_tree("/v2/game/tree/ad/view", access_token, {"play_id": int(time.time()), "ad_plat": 4})
        if res["status"] == "success": growth = res['data'].get('growth_increase', 0); res["message"] = f"施肥成功 (获得 {growth} 成长值)"; logging.info(f"[{token_short}] {res['message']}")
        elif res["status"] != "network_error": logging.info(f"[{token_short}] 施肥尝试结果: {res['message']}")
        return res
    @staticmethod
    def _watch_ad(access_token: str, ad_type: str = "tree_double", action: int = 2, page: str = "world", scene: Optional[str] = None) -> bool:
        token_short = access_token[:6]; logging.info(f"[{token_short}] 模拟观看广告: type={ad_type}, action={action}")
        params = {"play_id": int(time.time()), "action": action, "ad_id": ad_type, "page": page};
        if scene: params["scene"] = scene
        res = LoveTreeAPI._request_tree("/v1/game/tree/fairyland/hearts/ad/view", access_token, params)
        success = res["status"] == "success"; limit_reached = res["status"] == "ad_limit"
        if not success and not limit_reached and res["status"] != "network_error": logging.warning(f"[{token_short}] 看广告失败 (type={ad_type}): {res.get('message', '未知错误')}")
        elif limit_reached: logging.info(f"[{token_short}] 看广告 (type={ad_type}): {res.get('message', '广告次数达上限')}")
        elif success: logging.info(f"[{token_short}] 模拟看广告成功 (type={ad_type})")
        return success or limit_reached
    @staticmethod
    def collect_hearts(access_token: str, watch_ad: bool = True) -> Dict:
        token_short = access_token[:6]; logging.info(f"[{token_short}] 尝试领取容器爱心 (广告加倍: {watch_ad})...")
        ad_watched_successfully = False
        if watch_ad:
            ad_watched_successfully = LoveTreeAPI._watch_ad(access_token, ad_type="tree_double", action=2, page="world")
            if not ad_watched_successfully: logging.warning(f"[{token_short}] 容器爱心广告观看失败或达上限, 尝试普通领取...")
            else: time.sleep(random.uniform(0.5, 1.5))
        res = LoveTreeAPI._request_tree("/v1/game/tree/fairyland/hearts/vessel/take", access_token, {"type": 2, "by_ad": 1 if ad_watched_successfully else 0})
        if res["status"] == "success": hearts_got = res['data'].get('hearts', 0); prefix = "广告加倍" if ad_watched_successfully else "普通"; res["message"] = f"{prefix}领取容器爱心成功, 获得 {hearts_got} 爱心"; logging.info(f"[{token_short}] {res['message']}")
        elif res["status"] != "network_error": logging.info(f"[{token_short}] 领取容器爱心结果: {res['message']}")
        return res
    @staticmethod
    def take_random_hearts(access_token: str, watch_ad: bool = True) -> Dict:
        token_short = access_token[:6]; logging.info(f"[{token_short}] 尝试领取随机爱心 (广告加倍: {watch_ad})...")
        ad_watched_successfully = False
        if watch_ad:
            ad_watched_successfully = LoveTreeAPI._watch_ad(access_token, ad_type="plane", action=3, page="world", scene="fairyland")
            if not ad_watched_successfully: logging.warning(f"[{token_short}] 随机爱心广告观看失败或达上限, 尝试普通领取...")
            else: time.sleep(random.uniform(0.5, 1.5))
        res = LoveTreeAPI._request_tree("/v1/game/tree/fairyland/hearts/random/take", access_token, {"id": 0})
        if res["status"] == "success": hearts_got = res['data'].get('hearts', 0); prefix = "尝试广告后" if watch_ad else "普通"; res["message"] = f"{prefix}领取随机爱心成功, 获得 {hearts_got} 爱心"; logging.info(f"[{token_short}] {res['message']}")
        elif res["status"] != "network_error": logging.info(f"[{token_short}] 领取随机爱心结果: {res['message']}")
        return res
    @staticmethod
    def get_daily_login_reward(access_token: str, watch_ad: bool = True) -> Dict:
        token_short = access_token[:6]; logging.info(f"[{token_short}] 尝试领取每日登录奖励 (广告加倍: {watch_ad})...")
        ad_watched_successfully = False
        if watch_ad:
            ad_watched_successfully = LoveTreeAPI._watch_ad(access_token, ad_type="day", action=4, page="world")
            if not ad_watched_successfully: logging.warning(f"[{token_short}] 每日登录广告观看失败或达上限, 尝试普通领取...")
            else: time.sleep(random.uniform(0.5, 1.5))
        res = LoveTreeAPI._request_tree("/v1/game/tree/fairyland/login/reward", access_token, {"by_ad": 1 if ad_watched_successfully else 0})
        if res["status"] == "success": hearts_got = res['data'].get('hearts', 0); skin_msg = f", 获得皮肤ID: {res['data'].get('skins', [])}" if res['data'].get('skins') else ""; prefix = "广告加倍" if ad_watched_successfully else "普通"; res["message"] = f"{prefix}领取每日登录奖励成功, 获得 {hearts_got} 爱心{skin_msg}"; logging.info(f"[{token_short}] {res['message']}")
        elif res["status"] != "network_error": logging.info(f"[{token_short}] 领取登录奖励结果: {res['message']}")
        return res
    @staticmethod
    def get_tree_status(access_token: str) -> Optional[Dict]:
        token_short = access_token[:6]; logging.info(f"[{token_short}] 获取爱情树状态...")
        status_res = LoveTreeAPI._request_tree("/v2/game/tree/getInfo", access_token)
        if status_res["status"] == "success":
            data = status_res["data"]
            try:
                heart_vessel = data.get("heart_vessels", [{}])[0]
                status_data = {"level": data.get("level"), "growth": data.get("level_growth"), "next_level_growth": data.get("next_level_growth"), "stage": data.get("stage"), "next_stage_growth": data.get("next_stage_growth"), "consecutive_days": data.get("lasting_days"), "lover_consecutive_days": data.get("lover_lasting_days"), "hearts": heart_vessel.get("hearts"), "heart_capacity": heart_vessel.get("capacity"), "heart_left_count": heart_vessel.get("left_count"), "fertilizer_left": data.get("fertilizer_left", 0), "needs_water": data.get("lack_water") == 1, "needs_sun": data.get("lack_sunlight") == 1, "lover_needs_water": data.get("lover_lack_water") == 1, "lover_needs_sun": data.get("lover_lack_sunlight") == 1, "tree_code": data.get("tree_code"), "lover_name": data.get("lover_nick_name"), "lover_avatar": data.get("lover_head_pic")}
                logging.info(f"[{token_short}] 获取树状态成功: 等级={status_data['level']}, 成长={status_data['growth']}, 剩余肥料={status_data['fertilizer_left']}")
                return status_data
            except (IndexError, KeyError, TypeError) as e: logging.error(f"[{token_short}] 解析树状态时出错: {e} | 原始数据: {data}", exc_info=True); return None
        else: logging.error(f"[{token_short}] 获取树状态失败: {status_res.get('message', '未知错误')}"); return None
    @staticmethod
    def run_all_tree_tasks(access_token: str) -> List[Dict]:
        results = []; token_short = access_token[:6]; logging.info(f"[{token_short}] --- 开始执行爱情树任务组 ---")
        status_before = LoveTreeAPI.get_tree_status(access_token)
        if status_before is None: logging.error(f"[{token_short}] 无法获取初始树状态，部分任务可能无法正确执行。"); initial_fertilizer_left = 0; initial_needs_water = False; initial_needs_sun = False
        else: initial_fertilizer_left = status_before.get("fertilizer_left", 0); initial_needs_water = status_before.get("needs_water", False); initial_needs_sun = status_before.get("needs_sun", False)
        task_order = [("每日登录奖励", lambda: LoveTreeAPI.get_daily_login_reward(access_token, watch_ad=REPORT_SETTINGS["tree_watch_ads"])), ("浇水", lambda: LoveTreeAPI.daily_water(access_token), lambda: initial_needs_water), ("晒太阳", lambda: LoveTreeAPI.daily_sun(access_token), lambda: initial_needs_sun), ("随机爱心", lambda: LoveTreeAPI.take_random_hearts(access_token, watch_ad=REPORT_SETTINGS["tree_watch_ads"])), ("容器爱心", lambda: LoveTreeAPI.collect_hearts(access_token, watch_ad=REPORT_SETTINGS["tree_watch_ads"]))]
        for name, task_func, *condition_funcs in task_order:
            should_run = True; status_msg = ""
            if condition_funcs:
                condition_func = condition_funcs[0]
                try:
                    should_run = condition_func()
                    if not should_run:
                        if name == "浇水": status_msg = "树当前不需要浇水"
                        elif name == "晒太阳": status_msg = "树当前不需要晒太阳"
                        else: status_msg = "条件不满足或前置状态未知"
                except Exception as e: logging.error(f"[{token_short}] 检查任务 '{name}' 条件时出错: {e}"); should_run = False; status_msg = "条件检查出错"
            if should_run:
                try: results.append({"task_name": name, "result": task_func()})
                except Exception as e: logging.error(f"[{token_short}] 执行任务 '{name}' 时发生异常: {e}", exc_info=True); results.append({"task_name": name, "result": {"status": "error", "message": f"执行时异常: {e}"}})
            else: results.append({"task_name": name, "result": {"status": "skipped", "message": status_msg}}); logging.info(f"[{token_short}] 跳过任务 '{name}': {status_msg}")
        if REPORT_SETTINGS["tree_fertilize_enabled"]:
            max_attempts = REPORT_SETTINGS["tree_fertilize_attempts"]; fertilize_delay = REPORT_SETTINGS["tree_fertilize_delay"]; actual_attempts = min(max_attempts, initial_fertilizer_left)
            logging.info(f"[{token_short}] 开始处理施肥: 配置尝试 {max_attempts} 次, 初始剩余 {initial_fertilizer_left} 次, 实际尝试 {actual_attempts} 次")
            if actual_attempts > 0:
                successful_fertilizations = 0; total_growth_increase = 0; final_status = "success"; stop_reason = ""; attempt_details = []
                for i in range(actual_attempts):
                    logging.info(f"[{token_short}] 进行第 {i+1}/{actual_attempts} 次施肥尝试...")
                    res = LoveTreeAPI.fertilize(access_token); attempt_details.append(f"Attempt {i+1}: {res['status']} - {res.get('message', '')[:50]}")
                    if res["status"] == "success": successful_fertilizations += 1; total_growth_increase += res.get("data", {}).get("growth_increase", 0)
                    elif res["status"] in ["already_done", "ad_limit", "error", "condition_not_met", "network_error"]: final_status = "partial" if successful_fertilizations > 0 else "failure"; stop_reason = f"在第 {i+1} 次尝试时停止 (原因: {res.get('message', res['status'])})"; logging.warning(f"[{token_short}] {stop_reason}"); break
                    elif res["status"] != "success": final_status = "partial" if successful_fertilizations > 0 else "failure"; stop_reason = f"在第 {i+1} 次尝试时遇到未知状态停止 (状态: {res['status']}, 消息: {res.get('message', '')})"; logging.warning(f"[{token_short}] {stop_reason}"); break
                    if i < actual_attempts - 1: logging.info(f"[{token_short}] 施肥尝试结束，延迟 {fertilize_delay} 秒..."); time.sleep(fertilize_delay)
                summary_message = f"尝试 {actual_attempts} 次, 成功 {successful_fertilizations} 次";
                if total_growth_increase > 0: summary_message += f", 共增加 {total_growth_increase} 成长值."
                if stop_reason: summary_message += f" ({stop_reason})"
                if successful_fertilizations == actual_attempts and actual_attempts > 0: final_status_icon = "success"
                elif successful_fertilizations > 0: final_status_icon = "partial"
                elif actual_attempts > 0 : final_status_icon = "failure"
                else: final_status_icon = "skipped"
                results.append({"task_name": "施肥 (循环)", "result": {"status": final_status_icon, "message": summary_message}}); logging.info(f"[{token_short}] 施肥循环结束: {summary_message}")
            else: logging.info(f"[{token_short}] 无需施肥 (初始剩余 {initial_fertilizer_left} 次)."); results.append({"task_name": "施肥 (循环)", "result": {"status": "skipped", "message": f"无需施肥 (剩余 {initial_fertilizer_left} 次)"}})
        else: logging.info(f"[{token_short}] 配置中已禁用施肥。"); results.append({"task_name": "施肥 (循环)", "result": {"status": "disabled", "message": "配置中已禁用"}})
        logging.info(f"[{token_short}] --- 爱情树任务组执行完毕 ---"); return results

# ====================== 报告生成模块 ======================
class ReportGenerator:
    @staticmethod
    def generate_full_report_data(account: Dict) -> Optional[Dict]:
        access_token = account["access_token"]; account_name = account.get('name', '未知账号'); token_short = access_token[:6]; report_data = {"account": account, "success": False}; log_prefix = f"账号 '{account_name}' ({token_short}...)"
        logging.info(f"{log_prefix} 开始生成报告数据"); print(f"\n{EMOJI_MAP['loading']} --- 开始处理: {account_name} ({token_short}...) ---")
        user_info = Love520API.get_user_info(access_token)
        if not user_info: logging.error(f"{log_prefix} 无法获取用户信息，中止报告生成"); print(f"{EMOJI_MAP['failure']} {log_prefix} 无法获取用户信息，请检查 Token 或网络。"); return None
        report_data["user_info"] = ReportGenerator._parse_user_info(user_info); print(f"{EMOJI_MAP['check']} 获取用户信息成功")
        report_data["punch_result"] = Love520API.daily_punch(access_token); print(f"{EMOJI_MAP.get(report_data['punch_result']['status'], EMOJI_MAP['info'])} 每日打卡: {report_data['punch_result']['message']}")
        report_data["punch_stats"] = Love520API.get_punch_stats(access_token)
        if report_data["punch_stats"]: print(f"{EMOJI_MAP['check']} 获取打卡统计成功")
        else: print(f"{EMOJI_MAP['warning']} 获取打卡统计失败")
        print(f"{EMOJI_MAP['info']} 获取纪念日信息 (农历计算已移除)")
        report_data["anniversaries"] = Love520API.get_anniversaries(access_token)
        if report_data["anniversaries"] is not None: print(f"{EMOJI_MAP['check']} 获取纪念日信息成功")
        else: print(f"{EMOJI_MAP['warning']} 获取纪念日信息失败")
        logging.info(f"{log_prefix} 开始执行爱情树任务..."); print(f"{EMOJI_MAP['loading']} 开始执行爱情树任务...")
        report_data["tree_task_results"] = LoveTreeAPI.run_all_tree_tasks(access_token); print(f"{EMOJI_MAP['check']} 爱情树任务执行完毕")
        report_data["tree_status"] = LoveTreeAPI.get_tree_status(access_token)
        if report_data["tree_status"]: print(f"{EMOJI_MAP['check']} 获取最终爱情树状态成功")
        else: print(f"{EMOJI_MAP['warning']} 获取最终爱情树状态失败")
        logging.info(f"{log_prefix} 报告数据生成完毕"); report_data["success"] = True; return report_data

    @staticmethod
    def _parse_user_info(data: Dict) -> Dict:
        user = data.get("user", {}); lover = data.get("lover", {}); anni = data.get("anni", {})
        return {"couple": {"user_name": user.get("nick_name", "你"), "user_avatar": user.get("head_url"), "lover_name": lover.get("nick_name", "对方"), "lover_avatar": lover.get("head_url")}, "relationship": {"start_date": f"{anni.get('year', '?')}-{anni.get('month', '?'):02d}-{anni.get('day', '?'):02d}", "days_together": abs(anni.get("days_count", 0)), "desc": anni.get("desc", "我们的恋爱时光")}}

    # *** 修改这里：使用 initial_streak 并调整文本 ***
    @staticmethod
    def format_report_text_v4_no_lunar(report_data: Dict) -> Tuple[str, str]:
        """将报告数据格式化为推送标题和Markdown文本内容 (无农历，支持覆盖日期)"""
        if not report_data or not report_data.get("success"): return "情侣空间助手报告生成失败", "无法获取足够的数据生成报告，请检查日志。"
        try:
            account_name = report_data["account"].get("name", "情侣空间"); lover_mention = report_data["account"].get("lover_name") or report_data["user_info"]["couple"]["lover_name"]; now_str = get_current_datetime().strftime('%Y-%m-%d %H:%M')
            title = f"{account_name} {EMOJI_MAP['love']} {now_str}"; lines = []
            user_info = report_data["user_info"]; couple = user_info["couple"]; rel = user_info["relationship"]
            lines.append(f"**{EMOJI_MAP['couple']} {couple['user_name']} & {lover_mention} {EMOJI_MAP['heart']}**"); lines.append(f"_{rel['desc']}_"); lines.append(f"{EMOJI_MAP['calendar']} 在一起第 **{rel['days_together']}** 天 | {rel['start_date']}"); lines.append("---")
            punch_result = report_data["punch_result"]; punch_status_icon = EMOJI_MAP.get(punch_result["status"], EMOJI_MAP['warning']); lines.append(f"{punch_status_icon} **打卡:** {punch_result.get('message', '状态未知')}")
            if report_data.get("punch_stats"):
                stats = report_data["punch_stats"]
                lines.append(f"\n{EMOJI_MAP['stats']} **本月想你 ({stats['total_days']}天):**")
                # --- 使用 initial_streak 并修改描述 ---
                lines.append(f"- {EMOJI_MAP['check']} 已想你: {stats['punched_days']} 天 (连续想你: {stats['initial_streak']} 天)")
                # -------------------------------------
                lines.append(f"- {EMOJI_MAP['rocket']} 完成率: {stats['completion_rate']}%")
                if stats.get("calendar_viz"): lines.append(f"- 月历: `{stats['calendar_viz']}`")
            else: lines.append(f"\n{EMOJI_MAP['warning']} 未能获取本月打卡统计")
            lines.append("---")
            annis = report_data.get("anniversaries")
            if annis is not None:
                lines.append(f"{EMOJI_MAP['anni']} **重要日子提醒:**")
                if not annis: lines.append("- 暂无即将到来的重要日子信息。")
                else:
                    count = 0
                    for anni in annis:
                        if count >= REPORT_SETTINGS["max_anniversaries"]: lines.append(f"- (还有更多，最多显示 {REPORT_SETTINGS['max_anniversaries']} 条)"); break
                        emoji = EMOJI_MAP["birthday"] if anni["type"] == "birthday" else EMOJI_MAP['heart']
                        override_tag = EMOJI_MAP["override"] if anni.get('is_override') else ""
                        date_desc = f"{anni['desc']}{override_tag}"; full_date_info = f"`{anni['date']}`"
                        if anni["days_left"] is not None and anni["days_left"] >= 0:
                            day_info = f"还有 **{anni['days_left']}** 天"; target_date_str = anni.get('next_event_date_debug', '')
                            if anni["days_left"] == 0: day_info = "**就是今天!**"
                            if anni.get('is_override') and target_date_str != "None": day_info += f" (目标: {target_date_str})"
                            elif not anni.get('is_override') and target_date_str != "None": day_info += f" (下次: {target_date_str})"
                            lines.append(f"- {emoji} {date_desc} {full_date_info} - {day_info}")
                        else: past_days_info = f"已过 {anni['days_passed']} 天"; lines.append(f"- {emoji} {date_desc} {full_date_info} - {past_days_info}")
                        count += 1
            else: lines.append(f"{EMOJI_MAP['warning']} 获取重要日子信息失败")
            lines.append("---")
            lines.append(f"**{EMOJI_MAP['tree']} 爱情树小助手:**")
            tree_tasks = report_data.get("tree_task_results", [])
            if tree_tasks:
                lines.append("任务执行结果:")
                for task in tree_tasks:
                    task_name = task['task_name']; result = task['result']; status_icon = EMOJI_MAP.get(result.get('status', 'failure'), EMOJI_MAP['warning']); task_display_name = "施肥" if "施肥" in task_name else task_name
                    lines.append(f"- {status_icon} {task_display_name}: {result.get('message', '状态未知')}")
            else: lines.append("- 未执行任何爱情树任务")
            tree_status = report_data.get("tree_status")
            if tree_status:
                lines.append("\n最终状态:")
                lines.append(f"- {EMOJI_MAP['level']} 等级: {tree_status.get('level', '?')} (阶段 {tree_status.get('stage', '?')})"); lines.append(f"- {EMOJI_MAP['growth']} 成长: {tree_status.get('growth', '?')} / {tree_status.get('next_level_growth', '?')}")
                lines.append(f"- {EMOJI_MAP['heart']} 爱心: {tree_status.get('hearts', '?')} / {tree_status.get('heart_capacity', '?')} (可领次数 {tree_status.get('heart_left_count', '?')})"); lines.append(f"- {EMOJI_MAP['fertilizer']} 肥料: 剩余 {tree_status.get('fertilizer_left', '?')} 次")
                lines.append(f"- {EMOJI_MAP['check']} 连续浇水: 我 {tree_status.get('consecutive_days', '?')}天 | {tree_status.get('lover_name','对方')} {tree_status.get('lover_consecutive_days', '?')}天")
                needs = [];
                if tree_status.get("needs_water"): needs.append(f"{EMOJI_MAP['water']}需浇水")
                if tree_status.get("needs_sun"): needs.append(f"{EMOJI_MAP['sun']}需晒太阳")
                if tree_status.get("lover_needs_water"): needs.append(f"{EMOJI_MAP['water']}对方需浇水")
                if tree_status.get("lover_needs_sun"): needs.append(f"{EMOJI_MAP['sun']}对方需晒太阳")
                if needs: lines.append(f"- {EMOJI_MAP['warning']} 注意: {', '.join(needs)}")
                else: lines.append(f"- {EMOJI_MAP['success']} 树当前状态良好!")
            else: lines.append(f"\n- {EMOJI_MAP['warning']} 未能获取爱情树最终状态")
            return title, "\n".join(lines)
        except Exception as e: logging.error(f"格式化报告时发生严重错误: {e}", exc_info=True); return "情侣空间助手报告异常", f"格式化报告时遇到内部错误，请检查日志。\n错误信息: {e}"


# ====================== 微信推送模块 ======================
# ... WechatPusher 类保持不变 ...
class WechatPusher:
    API_URL = "https://wxpusher.zjiecode.com/api/send/message"
    @staticmethod
    def send_text(title: str, content: str) -> bool:
        if not WXPUSHER_APP_TOKEN or not WXPUSHER_UIDS: logging.warning("WxPusher 配置不完整 (APP_TOKEN 或 UIDS 缺失)，跳过推送"); print(f"{EMOJI_MAP['warning']} WxPusher 配置不完整，跳过推送"); return False
        if not isinstance(WXPUSHER_UIDS, list) or not all(isinstance(uid, str) for uid in WXPUSHER_UIDS): logging.error(f"WxPusher UIDs 配置格式错误，必须是字符串列表: {WXPUSHER_UIDS}"); print(f"{EMOJI_MAP['failure']} WxPusher UIDs 配置格式错误，必须是字符串列表!"); return False
        payload = {"appToken": WXPUSHER_APP_TOKEN, "content": content, "summary": title, "contentType": 3, "uids": WXPUSHER_UIDS}
        logging.info(f"准备推送消息到 WxPusher UIDs: {WXPUSHER_UIDS}"); print(f"{EMOJI_MAP['loading']} 正在尝试推送报告到 WxPusher ({len(WXPUSHER_UIDS)}个用户)...")
        response_data = make_request(WechatPusher.API_URL, method="POST", headers={'Content-Type': 'application/json;charset=utf-8'}, is_json=True, data=payload)
        if response_data and response_data.get("code") == 1000: logging.info("WxPusher 推送成功"); print(f"{EMOJI_MAP['success']} 报告已成功推送到 WxPusher！"); return True
        else:
            error_message = f"WxPusher 推送失败: {response_data}"; logging.error(error_message); print(f"{EMOJI_MAP['failure']} {error_message}")
            if response_data and isinstance(response_data, dict) and 'msg' in response_data: print(f"WxPusher 返回消息: {response_data['msg']}")
            return False

# ====================== 主程序 ======================
def main():
    start_time = time.time()
    print(f"\n{EMOJI_MAP['rocket']} {'='*10} 整合版 WeLove520 助手 v4.4 (月初连签/生日覆盖) {'='*10} {EMOJI_MAP['rocket']}")
    print(f"开始时间: {get_current_datetime().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"日志文件: {log_filename}")
    print(f"共配置 {len(ACCOUNTS)} 个账号")
    logging.info(f"=== 整合版 WeLove520 助手 v4.4 启动 | 共 {len(ACCOUNTS)} 个账号 (农历计算已移除) ===")
    if BIRTHDAY_OVERRIDES:
        print(f"{EMOJI_MAP['info']} 已配置 {len(BIRTHDAY_OVERRIDES)} 个生日日期覆盖:")
        for desc, target_date in BIRTHDAY_OVERRIDES.items(): print(f"  - '{desc}' -> {target_date}")
        logging.info(f"已配置生日覆盖: {BIRTHDAY_OVERRIDES}")
    successful_reports = 0; failed_accounts = 0
    for i, account in enumerate(ACCOUNTS):
        account_name = account.get("name", f"账号 {i+1}"); access_token_short = account.get("access_token", "未知Token")[:6]
        logging.info(f"--- 开始处理账号: {account_name} ({access_token_short}...) ---")
        try:
            report_data = ReportGenerator.generate_full_report_data(account)
            if report_data is None: failed_accounts += 1; continue
            report_title, report_content = ReportGenerator.format_report_text_v4_no_lunar(report_data) # Use the updated formatter
            print("\n--- 控制台报告预览 ---"); console_report = report_content.replace("**", "").replace("`", "").replace("_", ""); print(console_report); print("--- 报告预览结束 ---\n")
            if report_data.get("success"):
                 push_success = WechatPusher.send_text(report_title, report_content)
                 if push_success: successful_reports += 1
            else: print(f"{EMOJI_MAP['warning']} 报告数据生成不完整，跳过推送。")
        except Exception as e:
            failed_accounts += 1; error_msg = f"处理账号 {account_name} 时遇到未捕获的严重错误: {e}"; print(f"{EMOJI_MAP['failure']} {error_msg}")
            logging.exception(f"处理账号 {account_name} ({access_token_short}...) 时发生未捕获异常:")
        print(f"{EMOJI_MAP['done']} --- 账号: {account_name} 处理完毕 ---"); logging.info(f"--- 账号: {account_name} ({access_token_short}...) 处理完毕 ---")
        if i < len(ACCOUNTS) - 1: delay = random.uniform(5, 10); print(f"\n...暂停 {delay:.1f} 秒后处理下一个账号...\n"); time.sleep(delay)
    end_time = time.time(); duration = round(end_time - start_time, 2)
    print(f"\n{EMOJI_MAP['done']} {'='*15} 所有账号处理完毕 {'='*15} {EMOJI_MAP['done']}")
    print(f"结束时间: {get_current_datetime().strftime('%Y-%m-%d %H:%M:%S')}"); print(f"总耗时: {duration} 秒")
    processed_accounts = len(ACCOUNTS) - failed_accounts; print(f"成功生成并尝试推送报告数: {successful_reports} / {processed_accounts} (已处理)")
    if failed_accounts > 0: print(f"{EMOJI_MAP['failure']} 遇到严重错误导致处理失败的账号数: {failed_accounts}")
    logging.info(f"=== 整合版 WeLove520 助手 v4.4 运行结束 | 耗时: {duration}s | 处理成功: {processed_accounts} | 推送成功: {successful_reports} | 处理失败: {failed_accounts} ===")

if __name__ == "__main__":
    placeholders_found = False
    if any("YOUR_ACCESS_TOKEN" in acc.get("access_token", "") for acc in ACCOUNTS): print(f"\n{EMOJI_MAP['warning']} ************ 警告 ************\n{EMOJI_MAP['warning']} 检测到配置中有 'YOUR_ACCESS_TOKEN' 占位符！"); placeholders_found = True
    if "AT_YOUR_WXPUSHER_APP_TOKEN" == WXPUSHER_APP_TOKEN or not WXPUSHER_APP_TOKEN: print(f"\n{EMOJI_MAP['warning']} ************ 警告 ************\n{EMOJI_MAP['warning']} WXPUSHER_APP_TOKEN 未配置或为占位符！"); placeholders_found = True
    if any("UID_YOUR_UID" in uid for uid in WXPUSHER_UIDS) or not WXPUSHER_UIDS: print(f"\n{EMOJI_MAP['warning']} ************ 警告 ************\n{EMOJI_MAP['warning']} WXPUSHER_UIDS 未配置、为空或包含占位符！"); placeholders_found = True
    if placeholders_found: print(f"{EMOJI_MAP['warning']} *****************************"); logging.warning("检测到示例配置信息或配置缺失！")
    main()
