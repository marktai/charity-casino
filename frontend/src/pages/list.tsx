import React from 'react';
import CasinoService from '../api';
import { GameType } from '../api';
import {Container, Row, Col, ListGroup, Button} from 'react-bootstrap';
import {
  Link,
  useNavigate,
  useParams,
} from "react-router-dom";

type ListProps = {
  navigate: any,
  wordList: string,
}

type ListState = {
  people: null|Array<Object>,
  charities: null|Array<Object>,
  adult: null|boolean,
};

class List extends React.Component<ListProps, ListState> {
  state: ListState = {
    people: null,
    charities: null,
    adult: this.props.wordList === 'adult',
  };
  // ws: null|WebSocket = null;

  async refresh() {
    const people = await CasinoService.getPeople();
    const charities = await CasinoService.getCharities();
    this.setState({
      ...this.state,
      people: people,
      charities: charities,
    })
  }

  async refreshTimer(){
    this.refresh();
    setTimeout(() => {
      this.refreshTimer();
    }, 1000);
  }

  async componentDidMount() {
    await this.refreshTimer();

    // if (this.ws === null) {
    //   const ws_protocol = location.protocol === 'http:' ? 'ws:' : 'wss:';
    //   this.ws = new WebSocket(`${ws_protocol}//${window.location.host}/ws/listen/1`);
    //   this.ws.onmessage = async (event) => {
    //     const message: any = JSON.parse(event.data);
    //     if (message.type === 'LIST_UPDATE') {
    //       await this.refresh();
    //     }
    //   }
    // }
  }

  // async componentDidUpdate(prevProps: ListProps) {
  //   if (prevProps.wordList !== this.props.wordList) {
  //     this.setState({
  //       ...this.state,
  //       adult: this.props.wordList === 'adult',
  //     });
  //     await this.refresh();
  //   }
  // }

  // async newGame() {
  //   const newGame = await CasinoService.newGame(this.props.wordList);
  //   this.props.navigate(`/games/${newGame.id}/clues`);
  // }

  // clearAllState() {
  //   localStorage.clear();
  // }

  // getLink(game: GameType) {
  //   return "/games/" + game.id + (game.clues === null ? "/clues" : "/guess");
  // }

  numberWithCommas(number) {
    return (+number).toLocaleString()
  }

  attemptParseStyle(styleJson){
    try {
      return JSON.parse(styleJson);
    } catch {
      return {};
    }
  }

  render() {
    // const [gamesWithoutClues, gamesWithClues] = [
    //   (this.state.games ?? []).filter((g) => g.clues === null),
    //   (this.state.games ?? []).filter((g) => g.clues !== null),
    // ].map((list) => list.map(
    //   (game: GameType, i: number) => {
    //     let text = game.clues === null ?
    //       `Game ${game.id} without clues` :
    //       `Game ${game.id} by ${game.author} with ${game.suggested_num_cards} cards`;
    //     if (game.daily_set_time !== null) {
    //       const date = new Date(new Date(game.daily_set_time).toLocaleString('en-US', { timeZone: 'America/Los_Angeles' }));
    //       text += ` (${date.getMonth() + 1}/${date.getDate()}'s daily puzzle)`
    //     }
    //     return <ListGroup.Item key={i}>
    //       <Link to={this.getLink(game)}>{text}</Link>
    //     </ListGroup.Item>;
    // }));
    const topPeople = this.state.people !== null ?
          <Row className="top-people">
            <Col xs={6} md={4}>
              <div className="top-card top-card-1">
                <h1 className="number">1.  §{this.numberWithCommas(this.state.people[0]["Current Funny Munny"])}</h1>
                <img className="picture-icon" src={this.state.people[0]["Image Link"]}/>
                <div className="name">{this.state.people[0]["Name"]}</div>
                <div className="charity"><a href={this.state.people[0]["Charity Link"]}>{this.state.people[0]["Charity Category"] !== null ? this.state.people[0]["Charity Category"] : "Charity Link"}</a></div>
              </div>
            </Col>
            <Col xs={6} md={4}>
              <div className="top-card">
                <h1 className="number">2.  §{this.numberWithCommas(this.state.people[1]["Current Funny Munny"])}</h1>
                <img className="picture-icon" src={this.state.people[1]["Image Link"]}/>
                <div className="name">{this.state.people[1]["Name"]}</div>
                <div className="charity"><a href={this.state.people[1]["Charity Link"]}>{this.state.people[1]["Charity Category"] !== null ? this.state.people[1]["Charity Category"] : "Charity Link"}</a></div>
              </div>
            </Col>
            <Col xs={6} md={4}>
              <div className="top-card">
                <h1 className="number">3.  §{this.numberWithCommas(this.state.people[2]["Current Funny Munny"])}</h1>
                <img className="picture-icon" src={this.state.people[2]["Image Link"]}/>
                <div className="name">{this.state.people[2]["Name"]}</div>
                <div className="charity"><a href={this.state.people[2]["Charity Link"]}>{this.state.people[2]["Charity Category"] !== null ? this.state.people[2]["Charity Category"] : "Charity Link"}</a></div>
              </div>
            </Col>
          </Row> : <img className="loader" src="https://www.marktai.com/download/54689/ZZ5H.gif"/>

    const peopleList = this.state.people !== null ? <Row className="people-list">
      { this.state.people.map((person, i) => { 
        return <Col xs={12}>
          <Row className="person" style={this.attemptParseStyle(person["Style JSON"])}>
            <Col xs={1}>
              <h4>{i + 1}.</h4>
            </Col>
            <Col xs={5} md={3}>
              <img className="picture-icon" src={person["Image Link"]}/>

              <span className="name">{person["Name"]}</span>
            </Col>
            <Col xs={3} md={5}>
              §{this.numberWithCommas(person["Current Funny Munny"])}
            </Col>
            <Col xs={3}>
              <a href={person["Charity Link"]}>{person["Charity Category"] !== null ? person["Charity Category"] : "Charity Link"}</a>
            </Col>
          </Row>
        </Col>
      })}
    </Row>
    : null

    const charityList = this.state.charities !== null ? <Row className="charities-list">
      { this.state.charities.map((charity, i) => { 
        console.log(charity)
        return <Col xs={12}>
          <Row className="charity" style={charity["Style"]}>
            <Col xs={1}>
              <h4>{i + 1}.</h4>
            </Col>
            <Col xs={8} md={5}>
              <img className="picture-icon" src={charity["Image Link"]}/>

              <span className="name">{charity["Name"]}</span>
            </Col>
            <Col xs={2}>
              <h4>${this.numberWithCommas(charity["Real Money"])}</h4>
            </Col>
          </Row>
        </Col>
      })}
    </Row>
    : null

    return (
      <Container className={"list" + (this.props.wordList !== "default" ? ` ${this.props.wordList}` : "")}>
        { charityList }
        { topPeople }
        { peopleList }
      </Container>
    );
  }
}

type ListContainerProps = {
  wordList?: string,
}

const ListContainer: React.FunctionComponent<ListContainerProps> = (props) => {
  const navigate = useNavigate();
  const wordList = props.wordList || useParams().wordList as string || "default";
  return (<List navigate={navigate} wordList={wordList }></List>)
}

export default ListContainer;
