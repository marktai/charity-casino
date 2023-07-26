import { v4 as uuidv4 } from 'uuid';

export type AnswerType = [number, number];
export type CardType = [string, string, string, string];

export type GameType = {
  id: number,
  clues: null|Array<string>,
  answer: [
    AnswerType,
    AnswerType,
    AnswerType,
    AnswerType,
  ],
  answer_cards: [
    CardType,
    CardType,
    CardType,
    CardType,
  ],
  suggested_num_cards: null|number,
  suggested_possible_cards: null|Array<CardType>,
  created_time: string,
  last_updated_time: string,
  author: string,
  daily_set_time: null|string,
  adult: boolean,
  wordList: string,
};

export type BoardClientState = {
  id: number,
  board_id: number,
  created_time: string,
  data: any,
  client_id: string,
};

export type GuessResponseType = Array<number>;

type GuessResponse = {
  results: GuessResponseType,
};

export async function httpJson<T>(
  request: RequestInfo
): Promise<T> {
  const response = await fetch(
    request
  );
  return await response.json();
}

export function getJson<T>(
  path: string,
  args: RequestInit = { method: "GET" }
): Promise<T> {
  return httpJson<T>(new Request(path, args));
};

export function postJson<T>(
  path: string,
  body: any,
  args: RequestInit = {
    method: "POST",
    body: JSON.stringify(body),
    headers: {
      'Content-Type': 'application/json'
    },
  }
): Promise<T>  {
  return httpJson<T>(new Request(path, args));
};

export function patchJson<T>(
  path: string,
  body: any,
  args: RequestInit = {
    method: "PATCH",
    body: JSON.stringify(body),
    headers: {
      'Content-Type': 'application/json'
    },
  }
): Promise<T>  {
  return httpJson<T>(new Request(path, args));
};

export default class CasinoService {
  public static host = '/api';

  public static getPeople(): Promise<Object> {
    return getJson<Object>(`${this.host}/people`);
  }

  public static getCharities(): Promise<Object> {
    return getJson<Object>(`${this.host}/charities`);
  }

  public static updatePerson(person: Object): Promise<Object> {
    return patchJson<GameType>(`${this.host}/people`, person);
  }
}


interface HttpResponse<T> extends Response {
  parsedBody?: T;
}
