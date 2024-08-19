"""
Article (Data) Merge

The code:
1. Split all data into chunks.
2. Get the data embedding using `do_pooling()` with each data chunks.
3. Support `Doc2Vec`, `SBERT`, `BGE`, and `BGE-M3` models.
4. Calculate the similarity with FAISS.
"""

import argparse
import faiss
import os

import numpy as np

from FlagEmbedding import FlagModel
from typing import (
    Dict,
    List,
    Union,
)

from DataMerger import DataMerger
from DataProcessor import DataProcessor
from Doc2Vec import Doc2Vec
from SBERT import SBERT
from utils import (
    load_json,
    save_json,
)


def process(
    data: List[Dict[str, Union[int, List[str], List[List[str]], str]]],
    data_processor: DataProcessor,
    model: Union[Doc2Vec, FlagModel, SBERT],
    index: faiss.IndexFlatIP,
    params: Dict[str, Union[float, int, str]],
    is_topic_data: bool = False,
    use_local_lm: bool = True,
) -> None:
    """ Merge the given data.

    Args:
        data (List[Dict[str, Union[int, List[str], List[List[str]], str]]]): The data need to be processed.
        data_processor (DataProcessor): The data processor.
        model (Union[Doc2Vec, FlagModel, SBERT]): The language model which is used to get the sentence embedding.
        index (faiss.IndexFlatIP): The FAISS index.
        params (Dict[str, Union[float, int, str]]): The parameters.
        is_topic_data (bool, optional): Whether the given data is topic data. Defaults to False.
        use_local_lm (bool, optional): Whether to use the local language model to merge articles. Defaults to True.
    """

    all_data = []

    for i in range(len(data)):
        print(f"Processing {i}")

        data_key = "merge_content" if is_topic_data else "article_content"

        string_chunks = data_processor.get_string_chunks(
            text=data[i][data_key])

        one_data_chunks = []

        for j, string_chunk in enumerate(string_chunks):
            if params["model_name"] == "Doc2Vec":
                embedding_chunk = model.forward(
                    documents=[string_chunk])["documents_embedding"]
            elif params["model_name"] == "SBERT":
                embedding_chunk = model(
                    sentences=[string_chunk])["sentences_embedding"]
            elif params["model_name"] == "BGE":
                embedding_chunk = model.encode(string_chunk)

                embedding_chunk = np.array([embedding_chunk])
            elif params["model_name"] == "BGE-M3":
                embedding_chunk = model.encode(string_chunk)

                embedding_chunk = np.array([embedding_chunk])

            one_data_chunks.append({
                "string_chunk":
                string_chunk,
                "embedding_chunk":
                embedding_chunk.astype("float32"),
                "data_index":
                i,
                "chunk_index":
                j,
            })

        pooled_embedding = data_processor.do_pooling(
            embedding_chunks=[
                item["embedding_chunk"] for item in one_data_chunks
            ],
            pooling_type="mean",
        ).astype("float32")

        all_data.append({
            "article": data[i]["article_content"],
            "pooled_embedding": pooled_embedding,
            "data_index": i,
        })

        faiss.normalize_L2(pooled_embedding)

        index.add(pooled_embedding)

    over_threshold_data = []

    for i in range(len(all_data)):
        print(f"Processing {i}")

        faiss.normalize_L2(x=all_data[i]["pooled_embedding"])

        distances, indices = index.search(
            all_data[i]["pooled_embedding"],
            2,
        )

        search_results = [(
            index,
            float(distance),
        ) for distance, index in zip(
            distances[0],
            indices[0],
        )]

        if search_results[0][0] == i:
            if search_results[1][1] > params["similarity_threshold"]:
                over_threshold_data.append({
                    "base_data":
                    all_data[i]["article"]
                    if is_topic_data else [all_data[i]["article"]],
                    "base_data_index":
                    all_data[i]["data_index"],
                    "match_data":
                    all_data[search_results[1][0]]["article"] if is_topic_data
                    else [all_data[search_results[1][0]]["article"]],
                    "match_data_index":
                    all_data[search_results[1][0]]["data_index"],
                    "similarity":
                    search_results[1][1],
                })
        else:
            if search_results[0][1] > params["similarity_threshold"]:
                over_threshold_data.append({
                    "base_data":
                    all_data[i]["article"]
                    if is_topic_data else [all_data[i]["article"]],
                    "base_data_index":
                    all_data[i]["data_index"],
                    "match_data":
                    all_data[search_results[0][0]]["article"] if is_topic_data
                    else [all_data[search_results[0][0]]["article"]],
                    "match_data_index":
                    all_data[search_results[0][0]]["data_index"],
                    "similarity":
                    search_results[0][1],
                })

    data_merger = DataMerger(
        data=over_threshold_data,
        use_local_lm=use_local_lm,
        is_chunk=False,
    )

    merged_data = data_merger.merge()

    save_json(
        file_path=params["output_path"],
        data=merged_data,
    )

    print(
        f"The data number of the similarity over threshold ({params['similarity_threshold']}): {len(over_threshold_data)}"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-m",
        "--model",
        type=str,
        choices=[
            "Doc2Vec",
            "SBERT",
            "BGE",
            "BGE-M3",
        ],
        required=True,
        help="The model to use.",
    )
    parser.add_argument(
        "-dd",
        "--data_dir",
        type=str,
        required=True,
        help="The data directory.",
    )
    parser.add_argument(
        "-dn",
        "--data_name",
        type=str,
        required=True,
        help="The data name.",
    )
    parser.add_argument(
        "-t",
        "--topic",
        type=int,
        help="The topic number.",
    )
    parser.add_argument(
        "-op",
        "--output_path",
        type=str,
        required=True,
        help="The output path.",
    )
    parser.add_argument(
        "-st",
        "--similarity_threshold",
        type=float,
        default=0.875,
        help="The similarity threshold.",
    )
    parser.add_argument(
        "-ullm",
        "--use_local_lm",
        action="store_true",
        help="Whether to use the local language model.",
    )

    args = parser.parse_args()

    model = None
    index = None

    if args.model == "Doc2Vec":
        model = Doc2Vec()
        index = faiss.IndexFlatIP(100)
    elif args.model == "SBERT":
        model = SBERT()
        index = faiss.IndexFlatIP(768)
    elif args.model == "BGE":
        model = FlagModel(
            model_name_or_path="BAAI/bge-large-zh-v1.5",
            query_instruction_for_retrieval="为这个句子生成表示以用于检索相关文章：")
        index = faiss.IndexFlatIP(1024)
    elif args.model == "BGE-M3":
        model = FlagModel(
            model_name_or_path="BAAI/bge-m3",
            query_instruction_for_retrieval=
            "Generate a representation for this sentence for retrieving related articles:"
        )
        index = faiss.IndexFlatIP(1024)
    else:
        raise ValueError("The model is not supported.")

    data_processor = DataProcessor()

    data_dir = args.data_dir
    data_name = args.data_name

    data_path = os.path.join(
        data_dir,
        f"{data_name}.json",
    )

    data = load_json(file_path=data_path)

    print(f"Data {data_name} loaded successfully!")

    if not "topic" in data_name:
        params = {
            "model_name": args.model,
            "data_name": args.data_name,
            "topic": args.topic,
            "similarity_threshold": args.similarity_threshold,
            "output_path": args.output_path,
        }

        process(
            data=data,
            data_processor=data_processor,
            model=model,
            index=index,
            params=params,
            is_topic_data=False,
            use_local_lm=args.use_local_lm,
        )
    else:
        all_topic_data = {}

        for one_data in data:
            if not one_data["topic"] in all_topic_data.keys():
                all_topic_data[one_data["topic"]] = []

            all_topic_data[one_data["topic"]].append(one_data)

        for topic, topic_data in all_topic_data.items():
            if topic != args.topic:
                continue

            params = {
                "model_name": args.model,
                "data_name": args.data_name,
                "topic": args.topic,
                "similarity_threshold": args.similarity_threshold,
                "output_path": args.output_path,
            }

            process(
                data=topic_data,
                data_processor=data_processor,
                model=model,
                index=index,
                params=params,
                is_topic_data=True,
                use_local_lm=args.use_local_lm,
            )
