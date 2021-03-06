import importlib
import inspect
import json
import numbers
import os
import re
import sys

from django.core.exceptions import ImproperlyConfigured

__all__ = (
    'import_secrets',
)


def print_log(msg, show=True):
    if show:
        print(msg)


def import_secrets(secrets_obj=None, module=None, start=True, depth=0):
    """
    Python객체를 받아, 해당 객체의 key-value쌍을
    현재 모듈(config.settings.base)에 동적으로 할당

    1. dict거나 list일 경우에는 내부 값들이 eval()이 가능한지 검사해야 함
    2. value가 dict나 list가 아닐 경우에는
        2-1. eval()이 가능하다면 해당 결과를 할당
        2-2. eval()이 불가능하다면 (일반 텍스트나 숫자일 경우) 값 자체를 할당

    :param secrets_obj:
    :param module:
    :param start:
    :param depth:
    :return:
    """
    if not module:
        frame = inspect.stack()[1][0]
        module = inspect.getmodule(frame)

    show_log = getattr(module, 'PRINT_JSON_SETTINGS', False)

    # 불러올 JSON파일명
    file_name = module.__name__.split('.')[-1]

    if start:
        # logging.info('= Set JSON Secrets Start =')
        print_log('- JSON Secrets ({})'.format(
            file_name,
        ), show_log)

    def eval_obj(obj):
        """
        주어진 파이썬 객체의 타입에 따라 eval()결과를 반환하거나 불가한 경우 그냥 그 객체를 반환
        1. 그대로 반환
            - int, float형이거나 str형이며 숫자 변환이 가능한 경우에는 그대로 반환
            - eval()에서 예외가 발생했으며 없는 변수를 참조할때의 NameError가 발생한 경우
        2. eval() 평가값을 반환
            - 1번의 경우가 아니며 eval()이 가능한 경우 평가값을 반환
        3. 그대로 반환하되, 로그를 출력
            - 1번의 경우가 아니며 eval()에서 NameError외의 예외가 발생한 경우
        :param obj: 파이썬 객체
        :return: eval(obj)또는 obj
        """
        # 객체가 int, float거나
        if isinstance(obj, numbers.Number) or (
                # str형이면서 숫자 변환이 가능한 경우
                isinstance(obj, str) and obj.isdigit()):
            return obj

        # 객체가 int, float가 아니면서 숫자형태를 가진 str도 아닐경우
        try:
            return eval(obj)
        except NameError:
            # 없는 변수를 참조할 때 발생하는 예외
            return obj
        except Exception as e:
            # print_log(f'Cannot eval object({obj}), Exception: {e}', print_setting)
            return obj
            # raise ValueError(f'Cannot eval object({obj}), Exception: {e}')

    # SECRETS_MODULES의 내용을 현재 모듈(secrets_json)에 import
    try:
        modules_dict = getattr(module, 'SECRETS_MODULES', {})
        for key, value in modules_dict.items():
            if isinstance(value, str):
                setattr(sys.modules[__name__], key, importlib.import_module(value))
            else:
                setattr(sys.modules[__name__], key, value)
    except TypeError:
        raise ImproperlyConfigured('The SECRET_MODULES must Dictionary')

    # load한 JSON파일이 없는 경우
    if not secrets_obj:
        # 이 함수를 호출한 모듈에서 SECRETS_DIR정보를 가져와 json.loads실행
        try:
            frame = inspect.stack()[1][0]
            mod = inspect.getmodule(frame)
            secrets_dir = getattr(mod, 'SECRETS_DIR')
        except AttributeError:
            raise ImproperlyConfigured('The SECRET_DIR settings must exist')

        secrets_path = os.path.join(secrets_dir, f'{file_name}.json')
        secrets_obj = json.loads(open(secrets_path, 'rt').read())

    # base.json파일을 parsing한 결과 (Python dict)를 순회
    # set_config에 전달된 객체가 'dict'형태일 경우
    if isinstance(secrets_obj, dict):
        # key, value를 순회
        for key, value in secrets_obj.items():
            # value가 dict거나 list일 경우 재귀적으로 함수를 다시 실행
            if isinstance(value, dict) or isinstance(value, list):
                print_log(' {depth}{key}'.format(depth=' ' * depth, key=key), show_log)
                import_secrets(value, module, start=False, depth=depth + 1)
            # 그 외의 경우 value를 평가한 값을 할당
            else:
                secrets_obj[key] = eval_obj(value)
                # logging.info(f' settings.{key} = {value}')
                print_log(
                    ' {depth}{key} = {value}{value_type}'.format(
                        depth=' ' * depth,
                        key=key,
                        value=secrets_obj[key],
                        # value_type=f' (type: {type(secrets_obj[key])})'
                        value_type=''
                    ),
                    show_log
                )
            # set_config()가 처음 호출된 loop에서만 setattr()을 실행
            if start:
                setattr(module, key, value)
    # 전달된 객체가 'list'형태일 경우
    elif isinstance(secrets_obj, list):
        # list아이템을 순회하며
        for index, item in enumerate(secrets_obj):
            # list의 해당 index에 item을 평가한 값을 할당
            secrets_obj[index] = eval_obj(item)
            print_log(
                ' {depth}{item}'.format(
                    depth=' ' * depth,
                    item=secrets_obj[index],
                ),
                show_log
            )

    if depth == 0:
        print_log('', show_log)
        # 마지막 단계에서, import한 모듈에 djs_secrets_로 시작하는 속성(dict)이 있다면
        # 해당 속성을 마지막에 return해줄 객체와 합침
        # 마지막에 return할 dict가 우선이며, 없는 항목은 previous_에서 가져와 할당
        # **동시에 여러 module들을 import한 경우는 대비하지 않음
        setattr_prefix = 'djs_secrets_'
        p = re.compile(r'^{prefix}.*'.format(prefix=setattr_prefix))
        djs_name_list = list(filter(p.match, dir(module)))
        djs_name = djs_name_list[0] if djs_name_list else None

        if djs_name:
            previous_secrets_dict = getattr(module, djs_name)
            secrets_obj = dict(previous_secrets_dict, **secrets_obj)

        setattr_name = '{prefix}{name}'.format(
            prefix=setattr_prefix,
            name=module.__name__,
        )
        setattr(module, setattr_name, secrets_obj)
        return secrets_obj
