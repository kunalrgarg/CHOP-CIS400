import React, { Component } from 'react';
import * as RB from 'react-bootstrap';

class Home extends Component {
  render() {
    return (
      <div>
        <RB.Grid>
          <RB.Row>
            <RB.Col xs={4} md={2} />
            <RB.Col xs={12} md={8}>
              <RB.PageHeader>
                SCOSY - Top Secret Medical Project
                <br />
                <small>
                  by Santiago Buenahora, Garrett Darley, Kunal Garg, Nick Keenan
                </small>
              </RB.PageHeader>
            </RB.Col>
            <RB.Col xs={4} md={2} />
          </RB.Row>
        </RB.Grid>
      </div>
    )
  }
}

export default Home;
