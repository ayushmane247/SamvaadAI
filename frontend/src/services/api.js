// src/services/api.js

export const submitEligibilityAnswers = async (answers) => {
  /*
    Expected backend API:
    POST /api/eligibility

    Body:
    {
      occupation: string,
      income: number,
      landOwned: string
    }

    Expected Response:
    {
      status: "eligible" | "partial" | "not_eligible",
      schemes: [
        {
          id: "pm-kisan",
          name: "PM-KISAN Yojana",
          eligibilityScore: 85
        }
      ]
    }
  */
};

export const getSchemeDetails = async (schemeId) => {
  /*
    GET /api/schemes/:id

    Expected Response:
    {
      id: "pm-kisan",
      title: string,
      benefits: [],
      documents: [],
      applicationLink: string
    }
  */
};

export const saveConversation = async (payload) => {
  /*
    POST /api/conversation

    Body:
    {
      userId: string,
      messages: [],
      answers: {},
      language: string
    }
  */
};