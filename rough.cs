
    [Serializable]
    [DataContract]
    public class PA_Analysis
    {
        [DataMember]
        public int PAAnalysisID { get; set; } // Primary Key

        [DataMember]
        public int RecordSourceID { get; set; }

        [DataMember]
        public int RecordTypeEnum { get; set; }

        [DataMember]
        public string RecordTypeName { get; set; } // Max length 256

        [DataMember]
        public string Details { get; set; }

        [DataMember]
        public string Proposal { get; set; }

        [DataMember]
        public string OutcomeDescription { get; set; }

        [DataMember]
        public int ComplianceOutcomeEnum { get; set; }

        [DataMember]
        public string ComplianceOutcomeName { get; set; } // Max length 128

        [DataMember]
        public string AdditionalDetails { get; set; }
    }

[Serializable]
[DataContract]
public class PA_AnalysisHeader
{
    [DataMember]
    public int PA_AnalysisHeader_ID { get; set; } // Primary Key

    [DataMember]
    public int PA_Analysis_ID { get; set; } // Foreign Key

    [DataMember]
    public string Header { get; set; } // Max length 1024
}

[Serializable]
[DataContract]
public class PA_AnalysisTopic
{
    [DataMember]
    public int PA_AnalysisTopic_ID { get; set; }

    [DataMember]
    public int PA_AnalysisHeader_ID { get; set; }

    [DataMember]
    public string Topic { get; set; }
}

[Serializable]
[DataContract]
public class PA_AnalysisFinding
{
    [DataMember]
    public int PA_AnalysisFinding_ID { get; set; } // Primary Key

    [DataMember]
    public int PA_AnalysisTopic_ID { get; set; } // Foreign Key

    [DataMember]
    public string Finding { get; set; }

    [DataMember]
    public string Description { get; set; }

    [DataMember]
    public string Reason { get; set; }

    [DataMember]
    public string Action { get; set; }

    [DataMember]
    public int ComplianceOutcome_ENUM { get; set; }

    [DataMember]
    public string ComplianceOutcome_NAME { get; set; }

    [DataMember]
    public bool Flag_IsDescretionRequired { get; set; }

    [DataMember]
    public bool Flag_IsFIRequired { get; set; }

    [DataMember]
    public bool Flag_IsNotificationRequired { get; set; }

    [DataMember]
    public bool Flag_IsReferralRequired { get; set; }
}

[Serializable]
[DataContract]
public class PA_UserFeedback
{
    [DataMember]
    public int PA_AnalysisDetail_ID { get; set; }

    [DataMember]
    public int PA_AnalysisFinding_ID { get; set; }

    [DataMember]
    public int Contact_ID { get; set; }

    [DataMember]
    public int UserFeedback_ENUM { get; set; }

    [DataMember]
    public string UserFeedback_Name { get; set; }

    [DataMember]
    public string Comments { get; set; }
}
}

namespace AI_Handler.DTO
{
    [Serializable]
    [DataContract]
    public class ApiResponse : List<PA_AnalysisWithDetails>
    {
        // Custom methods or properties can be added here if needed
    }

    [Serializable]
    [DataContract]
    public class PA_AnalysisWithDetails : PA_Analysis
    {
        [DataMember]
        public List<PA_AnalysisHeaderWithTopics> AnalysisHeaders { get; set; }
    }

    [Serializable]
    [DataContract]
    public class PA_AnalysisHeaderWithTopics : PA_AnalysisHeader
    {
        [DataMember]
        public List<PA_AnalysisTopicWithFindings> AnalysisTopics { get; set; }
    }

    [Serializable]
    [DataContract]
    public class PA_AnalysisTopicWithFindings : PA_AnalysisTopic
    {
        [DataMember]
        public List<PA_AnalysisFindingWithFeedbacks> AnalysisFindings { get; set; }
    }

    [Serializable]
    [DataContract]
    public class PA_AnalysisFindingWithFeedbacks : PA_AnalysisFinding
    {
        [DataMember]
        public List<PA_UserFeedback> UserFeedbacks { get; set; }
    }
}


using HtmlAgilityPack;
using Newtonsoft.Json;
using AI_Handler.DTO;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;

namespace AI_Interface.Core
{
    public class AI_Interface : IDisposable
    {
        #region REST Connection settings
        private readonly HttpClient client = new HttpClient();
        private const string API_KEY = "0wvT4HJbHbvSXESp0vLru01J4fIukX5VqguxDgev";
        private const string SUMMARIZE_URL = "https://api.cohere.ai/v1/summarize";
        #endregion

        #region Public Functions

        public async Task<ApiResponse> Test()
        {
            string aiResponseAsJson = "";

            //Step 1 - Make a REST API call to get some raw data
            //Step 2 - Pack the data in json to assume AI system is returning data with our use case records

            #region Step 1
            aiResponseAsJson = await GetAIReponse();
            #endregion

            #region Step 2
            aiResponseAsJson = GetMockUpJson();

            // Deserialize the JSON directly into a List<PA_AnalysisWithDetails>
            var apiResponseList = JsonConvert.DeserializeObject<List<PA_AnalysisWithDetails>>(aiResponseAsJson);

            Console.WriteLine("Deserialization complete. Number of analyses: " + apiResponseList.Count);

            ApiResponse apiResponse = new ApiResponse();
            if (apiResponseList != null)
            {
                apiResponse.AddRange(apiResponseList);
            }
            #endregion


            #region step 3
            #endregion

            return apiResponse;
        }

        public void Dispose()
        {
            
        }
       
        #region Private Functions
        private string GetMockUpJson_old()
        {
            string jsonData = @"
            [
                {
                    'PA_Analysis_ID': 1,
                    'RecordSource_ID': 100,
                    'RecordType_ENUM': 1,
                    'RecordType_Name': 'Type A',
                    'Details': 'Analysis details here',
                    'Proposal': 'Proposal details here',
                    'OutcomeDescription': 'Outcome description here',
                    'ComplianceOutcome_ENUM': 0,
                    'ComplianceOutcome_NAME': 'Compliant',
                    'AnalysisDetails': [
                        {
                            'PA_AnalysisDetail_ID': 101,
                            'PA_Analysis_ID': 1,
                            'Header': 'Detail Header A',
                            'Topic': 'Topic A',
                            'Finding': 'Finding A',
                            'Description': 'Detailed description A',
                            'Reason': 'Reason for finding A',
                            'Action': 'Action plan A',
                            'ComplianceOutcome_ENUM': 0,
                            'ComplianceOutcome_NAME': 'Compliant',
                            'Flag_IsDescretionRequired': true,
                            'Flag_IsFIRequired': false,
                            'Flag_IsNotificationRequired': true,
                            'Flag_IsReferralRequired': false
                        },
                        {
                            'PA_AnalysisDetail_ID': 102,
                            'PA_Analysis_ID': 1,
                            'Header': 'Detail Header B',
                            'Topic': 'Topic B',
                            'Finding': 'Finding B',
                            'Description': 'Detailed description B',
                            'Reason': 'Reason for finding B',
                            'Action': 'Action plan B',
                            'ComplianceOutcome_ENUM': 1,
                            'ComplianceOutcome_NAME': 'Non-Compliant',
                            'Flag_IsDescretionRequired': false,
                            'Flag_IsFIRequired': true,
                            'Flag_IsNotificationRequired': true,
                            'Flag_IsReferralRequired': true
                        }
                    ]
                }
            ]";

            return jsonData;
        }

        private string GetMockUpJson()
        {
            string jsonData = @"[
                {
                    ""PAAnalysisID"": 1,
                    ""RecordSourceID"": 101,
                    ""RecordTypeEnum"": 1,
                    ""RecordTypeName"": ""TypeName1"",
                    ""Details"": ""Analysis Details 1"",
                    ""Proposal"": ""Proposal 1"",
                    ""OutcomeDescription"": ""Outcome 1"",
                    ""ComplianceOutcomeEnum"": 2,
                    ""ComplianceOutcomeName"": ""OutcomeName1"",
                    ""AdditionalDetails"": ""Some additional details 1"",
                    ""PA_AnalysisHeaders"": [
                        {
                            ""PA_AnalysisHeader_ID"": 201,
                            ""Header"": ""Header 1"",
                            ""PA_AnalysisTopics"": [
                                {
                                    ""PA_AnalysisTopic_ID"": 301,
                                    ""Topic"": ""Topic 1"",
                                    ""PA_AnalysisFindings"": [
                                        {
                                            ""PA_AnalysisFinding_ID"": 401,
                                            ""Finding"": ""Finding 1"",
                                            ""Description"": ""Description 1"",
                                            ""Reason"": ""Reason 1"",
                                            ""Action"": ""Action 1"",
                                            ""ComplianceOutcome_ENUM"": 3,
                                            ""ComplianceOutcome_NAME"": ""OutcomeName3"",
                                            ""Flag_IsDescretionRequired"": false,
                                            ""Flag_IsFIRequired"": true,
                                            ""Flag_IsNotificationRequired"": false,
                                            ""Flag_IsReferralRequired"": true,
                                            ""PA_UserFeedbacks"": [
                                                {
                                                    ""PA_AnalysisDetail_ID"": 501,
                                                    ""Contact_ID"": 601,
                                                    ""UserFeedback_ENUM"": 1,
                                                    ""UserFeedback_Name"": ""Positive Feedback"",
                                                    ""Comments"": ""Good job!""
                                                },
                                                {
                                                    ""PA_AnalysisDetail_ID"": 502,
                                                    ""Contact_ID"": 602,
                                                    ""UserFeedback_ENUM"": 2,
                                                    ""UserFeedback_Name"": ""Negative Feedback"",
                                                    ""Comments"": ""Needs improvement.""
                                                }
                                            ]
                                        },
                                        {
                                            ""PA_AnalysisFinding_ID"": 402,
                                            ""Finding"": ""Finding 2"",
                                            ""Description"": ""Description 2"",
                                            ""Reason"": ""Reason 2"",
                                            ""Action"": ""Action 2"",
                                            ""ComplianceOutcome_ENUM"": 4,
                                            ""ComplianceOutcome_NAME"": ""OutcomeName4"",
                                            ""Flag_IsDescretionRequired"": true,
                                            ""Flag_IsFIRequired"": false,
                                            ""Flag_IsNotificationRequired"": true,
                                            ""Flag_IsReferralRequired"": false,
                                            ""PA_UserFeedbacks"": [
                                                {
                                                    ""PA_AnalysisDetail_ID"": 503,
                                                    ""Contact_ID"": 603,
                                                    ""UserFeedback_ENUM"": 3,
                                                    ""UserFeedback_Name"": ""Neutral Feedback"",
                                                    ""Comments"": ""Average performance.""
                                                }
                                            ]
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
            ";    

            return jsonData;
        }

        private async Task<string> GetAIReponse()
        {
            string aiResponse = "";

            try
            {
                string text = GetSampleText();

                if (string.IsNullOrEmpty(text))
                {
                    Console.WriteLine("No text.");
                    return aiResponse;
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

                aiResponse = result.summary;

            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error: {ex.Message}");
            }
            return aiResponse;
            #endregion
        }

        private string GetSampleText()
        {
            return @"Local Park Hosts Successful Autumn Festival
                        Piara Waters, WA - April 30, 2025 - Residents of Piara Waters flocked to 
                        the local Discovery Park today for the annual Autumn Festival. The event, 
                        which ran from 10 am to 2 pm, featured live music from local bands, craft 
                        stalls showcasing handmade goods, and a variety of food trucks offering 
                        delicious treats. Children enjoyed face painting and bouncy castles, while 
                        families relaxed on picnic blankets enjoying the autumn sunshine. Organizers 
                        deemed the festival a great success, with higher than expected attendance. 
                        ""It was wonderful to see so many people from our community come together and 
                        enjoy the day,"" said Sarah Miller, a volunteer organizer. Proceeds from the 
                        event will go towards maintaining the park's facilities.";
        }

        #endregion

    }
}
