import bcrypt


class PwdUtil:
    """
    密码工具类
    """

    @classmethod
    def verify_password(cls, plain_password, hashed_password):
        """
        工具方法：校验当前输入的密码与数据库存储的密码是否一致

        :param plain_password: 当前输入的密码
        :param hashed_password: 数据库存储的密码
        :return: 校验结果
        """
        # bcrypt算法限制密码长度不能超过72字节，验证时也需要截断
        if plain_password is None:
            return False
        try:
            # 确保密码是字符串类型
            plain_password_str = str(plain_password)
            # 截断超过72字节的密码
            truncated_password = plain_password_str[:72]
            # 确保密码以字节形式传递
            password_bytes = truncated_password.encode('utf-8')
            # 确保哈希值以字节形式传递
            if isinstance(hashed_password, str):
                hashed_bytes = hashed_password.encode('utf-8')
            else:
                hashed_bytes = hashed_password
            return bcrypt.checkpw(password_bytes, hashed_bytes)
        except Exception as e:
            # 如果验证过程出现异常，记录并返回False
            from utils.log_util import logger
            logger.error(f'密码验证异常: {str(e)}')
            return False

    @classmethod
    def get_password_hash(cls, input_password):
        """
        工具方法：对当前输入的密码进行加密

        :param input_password: 输入的密码
        :return: 加密成功的密码
        """
        # bcrypt算法限制密码长度不能超过72字节
        if input_password is None:
            input_password = ''
        # 确保密码是字符串类型
        input_password_str = str(input_password)
        # 截断超过72字节的密码
        truncated_password = input_password_str[:72]
        # 生成盐值并加密
        password_bytes = truncated_password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        # 返回字符串形式的哈希值
        return hashed.decode('utf-8')
