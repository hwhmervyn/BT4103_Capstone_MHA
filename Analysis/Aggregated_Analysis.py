from Individual_Analysis import cleaned_findings_df
from llmConstants import chat
from langchain.schema.document import Document
from langchain.prompts import PromptTemplate
from langchain.chains.llm import LLMChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains import ReduceDocumentsChain, MapReduceDocumentsChain
from langchain.callbacks import get_openai_callback


def get_common_themes(df, llm):
    docs = df['Findings'].apply(lambda x: Document(page_content=x[4:])).tolist() # Remove <br> and convert to Document type

    with get_openai_callback() as usage_info:
        map_template = """The following is a set of documents
        {docs}
        Based on this list of docs, please identify the main themes'
        Helpful Answer:"""
        map_prompt = PromptTemplate.from_template(map_template)
        map_chain = LLMChain(llm=llm, prompt=map_prompt)

        reduce_template = """The following is set of summaries:
        {doc_summaries}
        Take these and distill it into a final, consolidated summary of the main themes'. 
        Helpful Answer:"""
        reduce_prompt = PromptTemplate.from_template(reduce_template)
        reduce_chain = LLMChain(llm=llm, prompt=reduce_prompt)
        
        # Takes a list of documents, combines them into a single string, and passes this to an LLMChain
        combine_documents_chain = StuffDocumentsChain(
            llm_chain=reduce_chain, document_variable_name="doc_summaries"
        )

        # Combines and iteravely reduces the mapped documents
        reduce_documents_chain = ReduceDocumentsChain(
            # This is final chain that is called.
            combine_documents_chain=combine_documents_chain,
            # If documents exceed context for `StuffDocumentsChain`
            collapse_documents_chain=combine_documents_chain,
            # The maximum number of tokens to group documents into.
            token_max=4000,
        )

        # Combining documents by mapping a chain over them, then combining results
        map_reduce_chain = MapReduceDocumentsChain(
            # Map chain
            llm_chain=map_chain,
            # Reduce chain
            reduce_documents_chain=reduce_documents_chain,
            # The variable name in the llm_chain to put the documents in
            document_variable_name="docs",
            # Return the results of the map steps in the output
            return_intermediate_steps=False,
        )

        result = map_reduce_chain.run(docs)
        total_input_tokens = usage_info.prompt_tokens
        total_output_tokens = usage_info.completion_tokens
        total_cost = usage_info.total_cost
        print(result, total_input_tokens, total_output_tokens, total_cost)

result_tup = get_common_themes(cleaned_findings_df, chat)
common_themes = result_tup[0]