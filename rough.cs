using System;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json;
using HtmlAgilityPack;

class Program
{
    private static readonly HttpClient client = new HttpClient();
    private const string API_KEY = "YOUR_API_KEY"; // Replace with your Cohere API key
    private const string SUMMARIZE_URL = "https://api.cohere.ai/v1/summarize";

    static async Task Main(string[] args)
    {
        try
        {
            string url = "https://www.bbc.com/news/articles/example"; // Replace with your URL
            string text = await FetchTextFromUrl(url);

            if (string.IsNullOrEmpty(text))
            {
                Console.WriteLine("No text extracted from URL.");
                return;
            }

            // Prepare request payload
            var payload = new
            {
                text = text,
                length = "medium",
                format = "paragraph",
                model = "summarize-xlarge",
                temperature = 0.3
            };

            // Set up HTTP request
            client.DefaultRequestHeaders.Clear();
            client.DefaultRequestHeaders.Add("Authorization", $"Bearer {API_KEY}");
            client.DefaultRequestHeaders.Add("Accept", "application/json");

            var content = new StringContent(
                JsonConvert.SerializeObject(payload),
                Encoding.UTF8,
                "application/json"
            );

            // Send request to Cohere Summarize API
            var response = await client.PostAsync(SUMMARIZE_URL, content);
            response.EnsureSuccessStatusCode();

            // Parse and display response
            var responseBody = await response.Content.ReadAsStringAsync();
            dynamic result = JsonConvert.DeserializeObject(responseBody);
            Console.WriteLine("Summary:");
            Console.WriteLine(result.summary);
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error: {ex.Message}");
        }
    }

    static async Task<string> FetchTextFromUrl(string url)
    {
        try
        {
            var html = await client.GetStringAsync(url);
            var doc = new HtmlDocument();
            doc.LoadHtml(html);

            // Extract text from <p> tags (adjust XPath as needed)
            var nodes = doc.DocumentNode.SelectNodes("//p");
            if (nodes == null) return "";

            var text = new StringBuilder();
            foreach (var node in nodes)
            {
                text.AppendLine(node.InnerText.Trim());
            }
            return text.ToString();
        }
        catch
        {
            return "";
        }
    }
}
