import wikipedia
import requests
from datetime import datetime


class WebSearchSkill:
    """
    Web search functionality using Wikipedia
    Can be extended to use other APIs
    """
    
    def __init__(self):
        print("🔧 Initializing Web Search skill...")
        # Set Wikipedia language
        wikipedia.set_lang("en")
        print("✅ Web Search ready")
    
    def search(self, query):
        """
        Search for information
        
        Args:
            query: Search query
            
        Returns:
            str: Response text with search results
        """
        if not query or not query.strip():
            return "I need something to search for. What would you like to know?"
        
        query = query.strip()
        print(f"🔍 Searching for: {query}")
        
        try:
            # Try Wikipedia first
            result = self._search_wikipedia(query)
            if result:
                return result
            
            # If Wikipedia fails, provide alternative
            return self._search_fallback(query)
            
        except Exception as e:
            print(f"❌ Search error: {e}")
            return f"I had trouble searching for {query}. Please try rephrasing your question."
    
    def _search_wikipedia(self, query):
        """
        Search Wikipedia
        
        Args:
            query: Search query
            
        Returns:
            str: Wikipedia summary or None if not found
        """
        try:
            # Try different search strategies
            search_results = wikipedia.search(query, results=5)
            
            if not search_results:
                return None
            
            # Try each result until we find one that works
            for page_title in search_results:
                try:
                    # Get page summary (first 3 sentences)
                    summary = wikipedia.summary(page_title, sentences=3)
                    
                    response = f"According to Wikipedia: {summary}"
                    return response
                    
                except wikipedia.exceptions.PageError:
                    continue
                except Exception:
                    continue
            
            # If all failed
            return None
            
        except wikipedia.exceptions.DisambiguationError as e:
            # Multiple possible pages
            options = e.options[:3]
            return f"I found multiple results for '{query}'. Did you mean: {', '.join(options)}?"
            
        except Exception as e:
            print(f"Wikipedia error: {e}")
            return None
    
    def _search_fallback(self, query):
        """
        Fallback when Wikipedia doesn't have results
        
        Args:
            query: Search query
            
        Returns:
            str: Fallback response
        """
        return f"I couldn't find detailed information about '{query}' in my knowledge base. Try asking a more specific question or search online."
    
    def search_definition(self, term):
        """
        Get definition of a term
        
        Args:
            term: Term to define
            
        Returns:
            str: Definition
        """
        try:
            # Search for the term
            page = wikipedia.page(term, auto_suggest=True)
            
            # Get first paragraph as definition
            paragraphs = page.content.split('\n\n')
            definition = paragraphs[0] if paragraphs else page.summary
            
            # Limit length
            if len(definition) > 500:
                definition = definition[:500] + "..."
            
            return f"{term}: {definition}"
            
        except Exception as e:
            return f"I couldn't find a definition for '{term}'."
    
    def get_quick_fact(self, query):
        """
        Get a quick fact about something
        
        Args:
            query: What to get facts about
            
        Returns:
            str: Quick fact
        """
        try:
            summary = wikipedia.summary(query, sentences=2)
            return f"Quick fact: {summary}"
        except:
            return f"I don't have quick facts about '{query}' right now."