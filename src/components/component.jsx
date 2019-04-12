import React, { Component } from 'react';
import * as RB from 'react-bootstrap';
import ZoomableBurst from './zoomableBurst';
import { Modal } from 'react-bootstrap';
import './style.css';

class Index extends Component {
  constructor(props, context) {
    super(props, context);

    this.clickHandler = this.clickHandler.bind(this);
    this.hideModal = this.hideModal.bind(this);

    this.state = {
      activeModal: null,
    };
  }

  clickHandler(e, index) {
    this.setState({ activeModal: index })
  }

  hideModal() {
      this.setState({ activeModal: null})
  }

  render() {
    const {
      updateSearchTerm,
      updateSearchType,
      requestSearch,
      searchTerm,
      searchType,
      results,
      requestRecs,
      recResults,
      recInProgress,
      inProgress } = this.props;

    const BUTTONS = ['Default']; // can add more buttons of various style

    function onSelectAlert(value) {
      updateSearchType(value);
    }
    if (results) {
      console.log(results);
    }

    function renderDropdownButton(title, i) {
      return (
        <RB.DropdownButton
          bsStyle={title.toLowerCase()}
          title={searchType}
          key={i}
          id={`dropdown-basic-${i}`}>
          <RB.MenuItem eventKey="Mesh"
            onSelect={onSelectAlert}>
              Mesh</RB.MenuItem>
          <RB.MenuItem eventKey="Author"
            onSelect={onSelectAlert}>
              Author</RB.MenuItem>
          <RB.MenuItem eventKey="Title"
            onSelect={onSelectAlert}>
              Title</RB.MenuItem>
          <RB.MenuItem divider />
          <RB.MenuItem eventKey="General Keyword"
            onSelect={onSelectAlert}>
            General Keyword
          </RB.MenuItem>
        </RB.DropdownButton>
      );
    }

    const typeButton = (
      <RB.ButtonToolbar>
        {BUTTONS.map(renderDropdownButton)}
      </RB.ButtonToolbar>
    );

    const viewRecResults = recInProgress ? <h4>loading</h4> : (recResults ?
     <div>
      <RB.Table bordered hover><tbody><tr>
          <td width="25%">Name</td>
          <td width="75%">Weight</td></tr>
          {recResults['collaborators'].map((item, key) => {
            return (
              <tr key = {key}>
              <td width="25%">{item['author'].name}</td>
              <td width="75%">
                <RB.ProgressBar min={0} max={100} now={Math.ceil(item.weight * 100)}
                                label={'' + Math.ceil(item.weight * 100) + '%'}>
                </RB.ProgressBar>
              </td>
            </tr>)})}
        </tbody>
      </RB.Table></div> : <h4></h4>)

    function getRoleBadges(roles) {
      roles = roles.replace('[', '').replace(']', '').split(', ')
      const badgeTexts = [
        ['CA', 'Chief Author'],
        ['OA', 'Ordinary Author'],
        ['PI', 'Principal Investigator']
      ].filter(role => roles.indexOf('\'' + role[0] + '\'') >= 0).map(role =>
        '' + role[1] + ' (' + roles.filter(r => r == '\'' + role[0] + '\'').length + ')');
      return badgeTexts.map(t => <RB.Badge key={t} className={'badge-pill badge-' + (t.indexOf('Chief Author') >= 0 ?
        'success' : t.indexOf('Ordinary Author') >= 0 ? 'secondary' : 'primary')}
      >{t}</RB.Badge>)
    }

    const clickHandler = this.clickHandler;

    const searchResultComponent = (results ?
      <div>
        <RB.Col xs={1} md={1} />
        <RB.Col xs={15} md={15}>
          <RB.Table striped bordered hover>
            <tbody>
              <tr>
                <td width="17%">Name</td>
                <td width="36%">Roles</td>
                <td width="47%">More Info</td>
              </tr>
              {results['authors'].map((item, key) => {
                return (
                  <tr key = {key}>
                    <td width="17%">{item.name}</td>
                    <td width="36%">{getRoleBadges(item.roles)}</td>
                    <td width="47%"><RB.Button onClick={function (e) {clickHandler(e, key); requestRecs(item.id)}}>View Recs</RB.Button></td>
                    <Modal id={key} show={this.state.activeModal === key} onHide={this.hideModal} bsSize="large">
                      <Modal.Header closeButton><Modal.Title>Recommendations for {item.name}</Modal.Title>
                      </Modal.Header>
                      <Modal.Body>{viewRecResults}</Modal.Body>
                      <Modal.Footer>
                      </Modal.Footer>
                    </Modal>
                  </tr>)})}</tbody></RB.Table>
        </RB.Col>
        <RB.Col xs={1} md={1} />
      </div> : <h1>no results</h1>);

    return (
      <div>
        <RB.Grid>
          <RB.Row>
            <RB.Col xs={4} md={2} />
            <RB.Col xs={12} md={8}>
              <RB.PageHeader>
                MACRE: Medical and Academic Collaboration Recommendation Engine
                <br />
                <small>
                  by Santiago Buenahora, Garrett Darley, Kunal Garg, Nick Keenan
                </small>
              </RB.PageHeader>
              <form>
                <RB.FormGroup controlId='search'>
                  <RB.Grid>
                    <RB.Row className ="show-grid">
                      <RB.ControlLabel><h4 className="move-right">Please enter a search term</h4></RB.ControlLabel>
                    </RB.Row>
                    <RB.Row className ="show-grid">
                      <RB.Col xs={12} md={6}>
                        <RB.FormControl
                          value={searchTerm}
                          onChange={e => updateSearchTerm(e.target.value)}
                        />
                      </RB.Col>
                      <RB.Col xs={6} md={4}>
                        {typeButton}
                      </RB.Col>
                    </RB.Row>
                  </RB.Grid>
                  <RB.HelpBlock className="move-right">This search term will be used for finding researcher data</RB.HelpBlock>
                </RB.FormGroup>
                <RB.Button className="move-right" onClick={() => requestSearch(searchTerm, searchType)}>{inProgress ? "Loading" : "Search"}</RB.Button>
                <hr/>
              </form>
            </RB.Col>
            <RB.Col xs={4} md={2} />
          </RB.Row>
          <RB.Row>
            {results ? searchResultComponent : <div>
              <RB.Col xs={4} md={2} />
              <RB.Col xs={12} md={8}>
                <svg width={800} height={800}></svg>
              </RB.Col>
              <RB.Col xs={4} md={2} />
            </div>}
          </RB.Row>
          <ZoomableBurst/>
        </RB.Grid>
      </div>
    )
  }
}

export default Index;
