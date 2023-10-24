import argparse
import json


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-fp',
        '--file_path',
        required=True,
    )
    parser.add_argument(
        '-m',
        '--mode',
        help='\"full\" or \"substr\"',
        required=True,
    )

    args = parser.parse_args()

    file_path = args.file_path
    mode = args.mode

    data = load_data(file_path=file_path)

    evalute(data=data, mode=mode)


def load_data(file_path: str) -> list[dict]:
    """Load evaluting data

    Args:
        file_path (str): Path to the evaluting data

    Returns:
        list[dict]: Evaluting data
    """

    with open(file=file_path, mode='r', encoding='UTF-8') as file:
        data = json.load(file)

        file.close()

    return data


def evalute(data: list[dict], mode: str):
    """Evalute the prediction

    Args:
        data (list[dict]): Evaluting data
        mode (str): "full" or "substr", "full" means the prediction string must be the same as the label string, "substr" means the prediction string can be a substring of the label string.

    Raises:
        Exception: Invalid mode
    """
    if mode == 'full':
        mip, mir, mif = check_full_string(data=data)
    elif mode == 'substr':
        mip, mir, mif = check_sub_string(data=data)
    else:
        raise Exception('Invalid mode.')

    print(f"micro-precision: {mip}")
    print(f"micro-recall: {mir}")
    print(f"micro-f1: {mif}")


def check_full_string(data: list[dict]) -> tuple[float, float, float]:
    """Check strings in prediction and label with full mode

    Args:
        data (list[dict]): Evaluting data

    Returns:
        tuple[float, float, float]: micro-precision, micro-recall, micro-f1
    """
    pres = []
    res = []

    for one_data in data:
        labels = []
        tp = 0
        fp = 0

        for label in one_data['label']:
            label_triple = label[1:-1].split(", ")

            if len(label_triple) == 3:
                labels.append(label_triple)

        for pred in one_data['prediction']:
            pred_triple = pred[1:-1].split(", ")

            if len(pred_triple) != 3:
                continue

            if pred_triple in labels:
                tp += 1
            else:
                fp += 1

        fn = len(labels) - tp

        pre, re = get_precision_recall(tp, fp, fn)
        pres.append(pre)
        res.append(re)

    data_number = len(data)
    micro_pre = sum(pres) / data_number
    micro_re = sum(res) / data_number

    micro_f1 = 0

    if (micro_pre + micro_re) > 0:
        micro_f1 = (2 * micro_pre * micro_re) / (micro_pre + micro_re)

    return micro_pre, micro_re, micro_f1


def check_sub_string(data: list[dict]) -> tuple[float, float, float]:
    """Check strings in prediction and label with substr mode

    Args:
        data (list[dict]): Evaluting data

    Returns:
        tuple[float, float, float]: micro-precision, micro-recall, micro-f1
    """
    pres = []
    res = []

    for one_data in data:
        labels = []
        tp = 0
        fp = 0

        for label in one_data['label']:
            label_triple = label[1:-1].split(", ")

            if len(label_triple) == 3:
                labels.append(label_triple)

        for pred in one_data['prediction']:
            pred_triple = pred[1:-1].split(", ")

            if len(pred_triple) != 3:
                continue

            label_triple_match = False

            for label_triple in labels:
                for index in range(3):
                    if (label_triple[index] not in pred_triple[index]) and \
                            (pred_triple[index] not in label_triple[index]):
                        break

                    if ((label_triple[index] in pred_triple[index]) or \
                            (pred_triple[index] in label_triple[index])) and \
                            index == 2:
                        label_triple_match = True

                if label_triple_match == True:
                    break

            if label_triple_match == True:
                tp += 1
            else:
                fp += 1

        fn = len(labels) - tp

        pre, re = get_precision_recall(tp, fp, fn)
        pres.append(pre)
        res.append(re)

    data_number = len(data)
    micro_pre = sum(pres) / data_number
    micro_re = sum(res) / data_number

    micro_f1 = 0

    if (micro_pre + micro_re) > 0:
        micro_f1 = (2 * micro_pre * micro_re) / (micro_pre + micro_re)

    return micro_pre, micro_re, micro_f1


def get_precision_recall(tp: int, fp: int, fn: int) -> tuple[float, float]:
    """Calculate precision and recall

    Args:
        tp (int): True positive
        fp (int): False positive
        fn (int): False negative

    Returns:
        tuple[float, float]: precision, recall
    """
    pre = 0
    re = 0

    if (tp + fp) > 0:
        pre = tp / (tp + fp)

    if (tp + fn) > 0:
        re = tp / (tp + fn)

    return pre, re


if __name__ == '__main__':
    main()
