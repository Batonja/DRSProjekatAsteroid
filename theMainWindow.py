from PyQt5.QtWidgets import QMainWindow,QLabel,QApplication,QLineEdit,QPushButton,QCheckBox
from PyQt5.QtGui import QImage,QPalette,QBrush,QFont,QPainter, QPixmap,QPen
from PyQt5.QtCore import QSize,Qt,QPointF,QThread, pyqtSignal,QRect,QEvent
from threading import Thread,Lock,RLock
from math import sin,cos,radians;
from spaceShip import SpaceShip;
import sys, time;
from tournamentPlayWait import PLAY_WAIT;
from asteroid import Asteroid
from random import randrange, randint
from moveRotate import MOVE_ROTATE;
from multiprocessing import Pool,Process
import threading
import queue


asteroids = []
asteroidLabels = []
smallAsteroidSize = 40;
mediumAsteroidSize = 60;
bigAsteroidSize = 80;
goldAsteroidTimer = 10
spaceShip = [SpaceShip(350,350,Qt.red),SpaceShip(350,350,Qt.green),SpaceShip(350,350,Qt.yellow),SpaceShip(350,350,Qt.magenta)]
theKeys = set();

class AsteroidsThread(QThread):
    signal = pyqtSignal()

    def run(self):
        count = 0
        while True:

            count += 1
            time.sleep(0.07)
            for a in asteroids:
                if a != 'DESTROYED':
                    if a.direction == 0:
                        a.posX = a.posX + a.speed
                        a.posY = a.posY + a.speed
                    else:
                        a.posX = a.posX - a.speed
                        a.posY = a.posY - a.speed
                    a.calculateMyMiddle();
                    a.asignMinAndMaxToAsteroid();

            self.signal.emit()

class BonusAsteroidThread(QThread):
    signal = pyqtSignal()

    def run(self):
        count = 0
        while True:
            count += 1
            time.sleep(goldAsteroidTimer)
            self.signal.emit()

green = (0,70,0);
class theMainWindow(QMainWindow):
    keyPressed = pyqtSignal(QEvent)
    def __init__(self):
        super().__init__();

        self.smallAsteroidPixMap = QPixmap('./images/asteroid1.png').scaled(smallAsteroidSize, smallAsteroidSize,Qt.IgnoreAspectRatio)
        self.mediumAsteroidPixMap = QPixmap('./images/asteroid1.png').scaled(mediumAsteroidSize, mediumAsteroidSize,Qt.IgnoreAspectRatio)
        self.bigAsteroidPixMap = QPixmap('./images/asteroid1.png').scaled(bigAsteroidSize, bigAsteroidSize, Qt.IgnoreAspectRatio)
        self.goldAsteroidPixmap = QPixmap('./images/gold_asteroid.png').scaled(bigAsteroidSize, bigAsteroidSize, Qt.IgnoreAspectRatio)

        self.asteroidCount = 1

        self.initUI();


    def initUI(self):
        self.mode = "INITIATING";
        self.setGeometry(200,200,750,750);
        background = QImage("./images/start_page.webp")
        background = background.scaled(QSize(750,750));

        self.scoreLabel = [QLabel('', self),QLabel('', self),QLabel('', self),QLabel('', self)]

        #self.scoreLabel.setGeometry(10, 10, 200, 50);
        #self.scoreLabel.setStyleSheet("font: 20pt Times new roman; color: green");
        #self.scoreLabel.hide()
        self.numberOfPlayers = 0
        self.points = 0
        self.currentLevel = 0

        palette = QPalette();
        palette.setBrush(QPalette.Window,QBrush(background))
        self.setPalette(palette);
        self.labelPlayers = QLabel("Players",self);
        self.labelPlayers.move(320, 250)
        self.labelPlayers.setFont(QFont("Times new roman",25));
        self.labelPlayers.setFixedSize(300,200);
        self.labelPlayers.setStyleSheet("color:white")
        self.inputNumbers = QLineEdit(self)
        self.inputNumbers.setGeometry(450,345,25,20);
        self.rect = QRect(300,250,200,300);
        self.startButton = QPushButton("Start",self);
        self.startButton.setGeometry(305,490,190,50);
        self.startButton.clicked.connect(self.setPlayers)
        self.tournamentTick = QCheckBox("",self);
        self.tournamentTick.setGeometry(450,370,100,100);
        self.tournamentLabel = QLabel("Tournament",self);
        self.tournamentLabel.move(320, 400)
        self.tournamentLabel.setFixedSize(125,35)
        self.tournamentLabel.setFont(QFont("Times new roman",18));
        self.tournamentLabel.setStyleSheet("color:white")
        self.tournament = False;

        self.livesLabel = [QLabel("Player 1: ", self), QLabel("Player 2: ", self), QLabel("Player 3: ", self),
                           QLabel("Player 4: ", self)];
        i = 0;
        colors = ['red','green','yellow','magenta'];
        colorNum = 0;
        for label in self.livesLabel:
            label.setGeometry(580, 10 + i, 200, 50);
            label.setStyleSheet("font: 20pt Times new roman; color:" + colors[colorNum]);
            colorNum += 1;
            i += 30;
            label.hide();

        self.lifeBox = [];


        self.show();

    def createBonusAsteroid(self):
        randomDirection = randint(0, 1)
        posX = randrange(1, 750)
        posY = randrange(1, 750)

        x = 200
        y = 200
        goldAsteroid = Asteroid(3, posX, posY, 3, randomDirection)
        goldAsteroid.points = 300
        golAsteroidLabel = QLabel(self)
        golAsteroidLabel.setPixmap(self.goldAsteroidPixmap)
        goldAsteroid.whatSizeAmI = 'BIG'
        golAsteroidLabel.setGeometry(posX, posY, 100, 100)

        asteroids.append(goldAsteroid)
        asteroidLabels.append(golAsteroidLabel)

        self.showAsteroids()

    def showAllLives(self):
        i = 1

        pixmaps = [QPixmap("./images/lives/redLife.png").scaled(20, 20),
                   QPixmap("./images/lives/greenLife.png").scaled(20, 20),
                   QPixmap("./images/lives/yellowLife.png").scaled(20, 20),
                   QPixmap("./images/lives/magentaLife.png").scaled(20, 20)]

        if(self.lifeBox.__len__() > 0):
            for box in self.lifeBox:
                box.hide();


        for num in range(self.numberOfPlayers):
            self.livesLabel[num].setText("Player " + i.__str__() + ": ");
            for j in range(spaceShip[i - 1].lives):
                self.lifeBox[j + (num*3)].setPixmap(pixmaps[i - 1])
                self.lifeBox[j + (num*3)].setGeometry(680 + (j * 20), 25 + (i - 1) * 30, 20, 20);
                self.lifeBox[j + (num*3)].show();

            i += 1;

            if self.livesLabel[num].isHidden():
                self.livesLabel[num].show()

    def setPlayers(self):
        if(self.inputNumbers.text() == '1' or self.inputNumbers.text() == '2' or self.inputNumbers.text() == '3' or self.inputNumbers.text() == '4') or self.tournamentTick.isChecked() == True:
            self.startAsteroids()
            #self.startBonus()

            if self.tournamentTick.isChecked():
                self.numberOfPlayers = 4;
            else:
                self.numberOfPlayers = self.inputNumbers.text();
                self.numberOfPlayers = int(self.numberOfPlayers);

            self.asteroidCountLabel = QLabel('Alive Count: ' + str(self.aliveAsteroidsCount()), self);
            self.asteroidCountLabel.setGeometry(10, 70, 200, 50);
            self.asteroidCountLabel.setStyleSheet("font: 20pt Times new roman; color: green");
            self.asteroidCountLabel.show()

            self.levelCountLabel = QLabel('', self);
            self.levelCountLabel.setGeometry(10, 100, 200, 50);
            self.levelCountLabel.setStyleSheet("font: 20pt Times new roman; color: green");
            self.levelCountLabel.show()

            self.startGame();
            self.rect.setHeight(0);
            self.rect.setWidth(0);
            self.startButton.hide();
            self.labelPlayers.hide();
            self.inputNumbers.focusWidget().clearFocus();
            self.inputNumbers.hide();
            self.tournamentLabel.hide();
            self.tournamentTick.hide();
            self.showScore();
            self.tournamentTick.focusWidget().clearFocus();
            if self.tournamentTick.isChecked():
                self.tournament = True;
                self.ucesnik1Index = self.generateRandomNumber([-1]);
                self.ucesnik2Index = self.generateRandomNumber([self.ucesnik1Index]);
                spaceShip[self.ucesnik1Index].tournamentPlaying = PLAY_WAIT.PLAY;
                spaceShip[self.ucesnik2Index].tournamentPlaying = PLAY_WAIT.PLAY;

                for i in range(spaceShip.__len__()):
                    if (i != self.ucesnik1Index and i != self.ucesnik2Index):
                        spaceShip[i].tournamentPlaying = PLAY_WAIT.WAIT;
            else:
                self.tournament = False;


            numOfLives = 3;
            for i in range(self.numberOfPlayers):
                self.scoreLabel[i].show();
                for j in range(numOfLives):
                    self.lifeBox.append(QLabel(self));




            self.showAllLives();
            self.repaint();

    def generateRandomNumber(self,number):
        exclude = number;
        randomNum = randint(0,3);
        return self.generateRandomNumber(number) if randomNum in exclude else randomNum;

    def paintEvent(self, e):
        qp = QPainter();
        qp.begin(self);
        lock = RLock()
        if self.tournament == False:
            for i in range(int(self.numberOfPlayers)):
                lock.acquire();
                if(spaceShip[i].lives > 0):
                    if(spaceShip[i].isDead == False ):
                        qp.setPen(spaceShip[i].color);
                        qp.drawLine(spaceShip[i].points[0], spaceShip[i].points[1]);
                        qp.drawLine(spaceShip[i].points[1], spaceShip[i].points[2]);
                        qp.drawLine(spaceShip[i].points[2], spaceShip[i].points[3]);
                        qp.drawLine(spaceShip[i].points[3], spaceShip[i].points[0]);
                        qp.drawLine(spaceShip[i].points[2], spaceShip[i].points[0]);
                        qp.setPen(QPen(spaceShip[i].colorOfProjectile))
                        qp.setBrush(QBrush(spaceShip[i].colorOfProjectile))
                        qp.drawEllipse(spaceShip[i].projectile, 5, 5);
                elif(spaceShip[i].isDead == False):
                    spaceShip[i].isDead = True;
                    spaceShip[i].x = None;
                    spaceShip[i].y = None;
                lock.release();
        else:
            for i in range(int(self.numberOfPlayers)):

                if(spaceShip[i].tournamentPlaying == PLAY_WAIT.PLAY and spaceShip[i].lives > 0):
                    qp.setPen(spaceShip[i].color);
                    qp.drawLine(spaceShip[i].points[0], spaceShip[i].points[1]);
                    qp.drawLine(spaceShip[i].points[1], spaceShip[i].points[2]);
                    qp.drawLine(spaceShip[i].points[2], spaceShip[i].points[3]);
                    qp.drawLine(spaceShip[i].points[3], spaceShip[i].points[0]);
                    qp.drawLine(spaceShip[i].points[2], spaceShip[i].points[0]);
                    qp.setPen(QPen(spaceShip[i].colorOfProjectile))
                    qp.setBrush(QBrush(spaceShip[i].colorOfProjectile))
                    qp.drawEllipse(spaceShip[i].projectile, 5, 5);

        qp.setBrush(QBrush(Qt.black));
        qp.drawRect(self.rect);

    def startGame(self):
        self.mode = "PLAYING";
        if(self.numberOfPlayers == '1'):
            del spaceShip[-1];
        background = QImage("./images/space.jpg")
        background = background.scaled(750,750);
        palette = QPalette();
        palette.setBrush(QPalette.Window,QBrush(background));
        self.setPalette(palette);

        #OVDE se pokrece checkIfDead !!!
        check = Thread(target=self.checkIfDead,args=());
        check.start();

        self.repaint()


    def moveIt(self):
        for x in range(10):
            spaceShip.move();
            self.repaint();

    def rotate_spaceShip(self,angle,spaceShip):
        i = 0;
        for point in spaceShip.points:
            (x, y) = spaceShip.rotate_point(point, angle, MOVE_ROTATE.ROTATE,
                                                    (spaceShip.x, spaceShip.y))
            spaceShip.points[i] = QPointF(x, y);
            i += 1;
        (vecX, vecY) = spaceShip.rotate(spaceShip.vector, angle)
        spaceShip.vector.setX(vecX);
        spaceShip.vector.setY(vecY);

        return spaceShip;

    def puppetShow(self):

        if Qt.Key_Up in theKeys and self.mode == "PLAYING" and spaceShip[0].isDead == False and spaceShip[
            0].tournamentPlaying != PLAY_WAIT.WAIT:
            # moving = multiprocessing.Process(target=self.spaceShip[0].move(),args=());
            # moving.start()


            spaceShip[0].move();

            self.repaint();

        if Qt.Key_W in theKeys and self.mode == "PLAYING" and int(self.numberOfPlayers) > 1 and spaceShip[
            1].isDead == False and spaceShip[1].tournamentPlaying != PLAY_WAIT.WAIT:
            # moving = multiprocessing.Process(target=self.spaceShip[0].move(), args=());
            # moving.start()

            spaceShip[1].move();

            self.repaint();
        if  Qt.Key_I in theKeys and self.mode == "PLAYING" and int(self.numberOfPlayers) > 2 and spaceShip[
            2].isDead == False and spaceShip[2].tournamentPlaying != PLAY_WAIT.WAIT:
            # moving = multiprocessing.Process(target=self.spaceShip[0].move(), args=());
            # moving.start()
            spaceShip[2].move();
            self.repaint();
        if Qt.Key_8  in theKeys  and self.mode == "PLAYING" and int(self.numberOfPlayers) > 3 and spaceShip[
            3].isDead == False and spaceShip[3].tournamentPlaying != PLAY_WAIT.WAIT:
            # moving = multiprocessing.Process(target=self.spaceShip[0].move(), args=());
            # moving.start()
            spaceShip[3].move();
            self.repaint();
        if (Qt.Key_Left  in theKeys  and self.mode == "PLAYING" and spaceShip[0].tournamentPlaying != PLAY_WAIT.WAIT) or (
                Qt.Key_Right in theKeys  and self.mode == "PLAYING" and spaceShip[0].isDead == False and spaceShip[
            0].tournamentPlaying != PLAY_WAIT.WAIT):
            angle = 0;
            if (Qt.Key_Left  in theKeys ):
                angle = -10;
            else:
                angle = 10

            spaceShip[0] = self.rotate_spaceShip(angle, spaceShip=spaceShip[0]);

            self.repaint();
        if ((Qt.Key_A  in theKeys  and self.mode == "PLAYING" and spaceShip[1].tournamentPlaying != PLAY_WAIT.WAIT) or (
                Qt.Key_D  in theKeys  and self.mode == "PLAYING" and spaceShip[
            1].tournamentPlaying != PLAY_WAIT.WAIT)) and int(self.numberOfPlayers) > 1 and spaceShip[1].isDead == False:
            angle = 0;
            if (Qt.Key_A  in theKeys ):
                angle = -10;
            else:
                angle = 10
            spaceShip[1] = self.rotate_spaceShip(angle, spaceShip=spaceShip[1]);

            self.repaint();
        if ((Qt.Key_J  in theKeys  and self.mode == "PLAYING" and spaceShip[2].tournamentPlaying != PLAY_WAIT.WAIT) or (
                Qt.Key_L  in theKeys  and self.mode == "PLAYING" and spaceShip[
            2].tournamentPlaying != PLAY_WAIT.WAIT)) and int(self.numberOfPlayers) > 2 and spaceShip[2].isDead == False:
            angle = 0;
            if (Qt.Key_J  in theKeys ):
                angle = -10;
            else:
                angle = 10
            spaceShip[2] = self.rotate_spaceShip(angle, spaceShip=spaceShip[2]);

            self.repaint();
        if ((Qt.Key_4 in theKeys  and self.mode == "PLAYING" and spaceShip[3].tournamentPlaying != PLAY_WAIT.WAIT) or (
                Qt.Key_6  in theKeys  and self.mode == "PLAYING" and spaceShip[
            3].tournamentPlaying != PLAY_WAIT.WAIT)) and int(self.numberOfPlayers) > 3 and spaceShip[3].isDead == False:
            angle = 0;
            if (Qt.Key_4  in theKeys ):
                angle = -10;
            else:
                angle = 10
            spaceShip[3] = self.rotate_spaceShip(angle, spaceShip=spaceShip[3]);

            self.repaint();
        if (Qt.Key_NumLock  in theKeys  and spaceShip[0].tournamentPlaying != PLAY_WAIT.WAIT):
            l = RLock();
            l.acquire();
            que = queue.Queue();
            t = Thread(target=self.shoot,args=(spaceShip[0],que))
            t.start();
            t.join();
            l.release();


        if (Qt.Key_Space  in theKeys  and int(self.numberOfPlayers) > 1 and spaceShip[
            1].tournamentPlaying != PLAY_WAIT.WAIT):
            l = RLock();
            l.acquire();
            que = queue.Queue();
            t = Thread(target=self.shoot, args=(spaceShip[1], que))
            t.start();
            t.join();
            l.release();
        

        if (Qt.Key_Delete  in theKeys  and int(self.numberOfPlayers) > 2 and spaceShip[
            2].tournamentPlaying != PLAY_WAIT.WAIT):
            l = RLock();
            l.acquire();
            que = queue.Queue();
            t = Thread(target=self.shoot, args=(spaceShip[2], que))
            t.start();
            t.join();
            l.release();

        if (Qt.Key_Plus  in theKeys  and int(self.numberOfPlayers) > 3 and spaceShip[
            3].tournamentPlaying != PLAY_WAIT.WAIT):
            l = RLock();
            l.acquire();
            que = queue.Queue();
            t = Thread(target=self.shoot, args=(spaceShip[3], que))
            t.start();
            t.join();
            l.release();


    def keyPressEvent(self, e):
        lock = RLock();
        if self.mode == "PLAYING":
            lock.acquire();
            theKeys.add(e.key())
            t = Thread(target=self.puppetShow,args=());
            t.start();
            t.join();
            lock.release();
    def keyReleaseEvent(self, e):
        lock = RLock();
        if(self.mode == "PLAYING"):
            if(theKeys.__contains__(e.key())):
                lock.acquire();
                theKeys.remove(e.key());
                lock.release();
    def shoot(self,ship,queue):
        ship.colorOfProjectile = ship.color;
        ship.projectile = QPointF(ship.points[0]);
        lock = RLock();
        while ((ship.projectile.x() < 760 and ship.projectile.x() > -10) and(ship.projectile.y() < 760 and ship.projectile.y() > -10))  :
            ship.projectile.setX(ship.projectile.x() + ship.vector.x() * ship.velocity);
            ship.projectile.setY(ship.projectile.y() + ship.vector.y() * ship.velocity);
            for i in range (len(asteroids)):
                if( asteroids[i] != 'DESTROYED' and (ship.projectile.x() >= asteroids[i].theMiddleX  - (asteroids[i].posMaxX - asteroids[i].posMinX)  and ship.projectile.x() <= asteroids[i].theMiddleX + (asteroids[i].posMaxX - asteroids[i].posMinX)) and (ship.projectile.y() >= asteroids[i].theMiddleY - (asteroids[i].posMaxY - asteroids[i].posMinY) and ship.projectile.y() <= asteroids[i].posMaxY + (asteroids[i].posMaxY - asteroids[i].posMinY))):
                    ship.reloadProjectile();
                    self.destroyAsteroid(asteroids[i],ship)
                    self.repaint()
                    queue.put(ship);
                    return ship;
            self.repaint();
        ship.reloadProjectile()
        queue.put(ship)
        return ship;


    def checkIfDead(self):
        found = False;
        lock = RLock();
        while True:
            time.sleep(0.07)
            for num in range(self.numberOfPlayers):

                found = False;
                if(spaceShip[num].isDead == False):
                    for point in spaceShip[num].points:
                        for i in range(len(asteroids)):
                            if (asteroids[i] != 'DESTROYED' and asteroids[i].isHidden == False and point.x() <= asteroids[i].posMaxX and point.x() >=
                                    asteroids[i].posMinX and point.y() >= asteroids[i].posMinY and point.y() <=
                                    asteroids[i].posMaxY and spaceShip[num].justSpawnedTimer == 0):
                                spaceShip[num].die();
                                lock.acquire();
                                self.showAllLives()
                                self.repaint();
                                lock.release();
                                spaceShip[num].justSpawnedTimer = 5;
                                t = Thread(target=spaceShip[num].countDownSpawnedTimer(),args=())
                                t.start();
                                t.join()
                                print("preziveo repaint");
                                found = True;
                                break;


                        if found:
                            break;

    def startAsteroids(self):
        #self.createAsteroids()
        self.thread = AsteroidsThread()
        self.thread.signal.connect(self.update)
        self.thread.start()


    def startBonus(self):
        self.bonusThread = BonusAsteroidThread()
        self.bonusThread.signal.connect(self.createBonusAsteroid)
        self.bonusThread.start()

    def update(self):
        self.asteroidCountLabel.setText('Alive: ' + str(self.aliveAsteroidsCount()))
        self.createAsteroids()

        for l in asteroidLabels:
            if l != 'DESTROYED':
                l.hide()

        for i in range(len(asteroids)):
            if asteroids[i] != 'DESTROYED':
                if asteroids[i].isHidden == False:
                    if asteroids[i].posX > self.frameGeometry().height():
                        asteroids[i].posX = 0
                    elif asteroids[i].posX <= 0:
                        asteroids[i].posX = 750
                    if asteroids[i].posY > self.frameGeometry().width():
                        asteroids[i].posY = 0
                    elif asteroids[i].posY <= 0:
                        asteroids[i].posY = 750
                    asteroidLabels[i].setGeometry(asteroids[i].posX, asteroids[i].posY, 100, 100)
                    asteroidLabels[i].show()

    def createAsteroids(self):
        if self.aliveAsteroidsCount() == 0:
            self.currentLevel += 1
            self.levelCountLabel.setText('Level: ' + str(self.currentLevel))

            #Na svakom nivou ima 2 vise asteroida
            self.asteroidCount += 20

            for i in range(self.asteroidCount):
                randomDirection = randint(0, 1)
                posX = randrange(1, 750)
                posY = randrange(1, 750)
                size = randrange(1, 4)
                asteroid = Asteroid(size, posX, posY, 3, randomDirection)

                lab = QLabel(self)

                if size == 1:
                    lab.setPixmap(self.smallAsteroidPixMap)
                    asteroid.whatSizeAmI = 'SMALL';
                elif size == 2:
                    lab.setPixmap(self.mediumAsteroidPixMap)
                    asteroid.whatSizeAmI = 'MEDIUM';
                    a = Asteroid(1, 1, 1, 3, 0);
                    a.whatSizeAmI = 'SMALL'
                    a.isHidden = True;
                    a.wasHidden = True
                    a1 = Asteroid(1, 2, 2, 3, 1);
                    a1.whatSizeAmI = 'SMALL'
                    a1.wasHidden = True
                    a1.isHidden = True;
                    asteroids.append(a);
                    asteroids.append(a1);
                    l = QLabel(self);
                    l.setPixmap(self.smallAsteroidPixMap);
                    l1 = QLabel(self);
                    l1.setPixmap(self.smallAsteroidPixMap);
                    asteroidLabels.append(l);
                    asteroidLabels.append(l1);
                else:
                    lab.setPixmap(self.bigAsteroidPixMap)
                    asteroid.whatSizeAmI = 'BIG';
                    a = Asteroid(2, 3, 3, 3, 0);
                    a.whatSizeAmI = 'MEDIUM'
                    a.isHidden = True;
                    a.wasHidden = True
                    a1 = Asteroid(2, 4, 4, 3, 1);
                    a1.whatSizeAmI = 'MEDIUM'
                    a1.wasHidden = True
                    a1.isHidden = True;
                    asteroids.append(a);
                    asteroids.append(a1);
                    l = QLabel(self);
                    l.setPixmap(self.mediumAsteroidPixMap);
                    l1 = QLabel(self);
                    l1.setPixmap(self.mediumAsteroidPixMap);
                    asteroidLabels.append(l);
                    asteroidLabels.append(l1);

                lab.setGeometry(asteroid.posX,asteroid.posY,100,100);
                asteroids.append(asteroid)
                asteroidLabels.append(lab)

            self.showAsteroids()

    def showAsteroids(self):
        for i in range(len(asteroidLabels)):
            if asteroidLabels[i] != 'DESTROYED':
                if asteroids[i].isHidden == False:
                    asteroidLabels[i].show()

    def showScore(self):
        i = 1;
        colors = ['red', 'green', 'yellow', 'magenta'];
        for num in range(self.numberOfPlayers):
            self.scoreLabel[num].hide()
            self.scoreLabel[num].setText("Score(Player " + i.__str__() + "): " + spaceShip[num].score.__str__());
            self.scoreLabel[num].setGeometry(20,20 + (num * 30),300,30);
            self.scoreLabel[num].setStyleSheet("font: 20pt Times new roman; color:" + colors[num]);
            self.scoreLabel[num].show();
            i += 1;


    def destroyAsteroid(self, asteroid,ship):
        asteroidIndex = asteroids.index(asteroid);
        ship.score += asteroid.points
        self.showScore()

        if asteroid.size == 1:
            asteroids[asteroidIndex] = 'DESTROYED'
            asteroidLabels[asteroidIndex].hide()
            asteroidLabels[asteroidIndex] = 'DESTROYED'
            print('Small asteroid has been destroyed')
        elif asteroid.size == 2 and asteroid.wasHidden == False:
            if asteroids[asteroidIndex - 2] != 'DESTROYED':
                asteroids[asteroidIndex - 2].isHidden = False
                asteroids[asteroidIndex - 2].posX = asteroid.posX
                asteroids[asteroidIndex - 2].posY = asteroid.posY
            if asteroids[asteroidIndex - 1] != 'DESTROYED':
                asteroids[asteroidIndex - 1].isHidden = False
                asteroids[asteroidIndex - 1].posX = asteroid.posX
                asteroids[asteroidIndex - 1].posY = asteroid.posY

            asteroids[asteroidIndex] = 'DESTROYED'
            asteroidLabels[asteroidIndex].hide()
            asteroidLabels[asteroidIndex] = 'DESTROYED'
            print('Medium asteroid has been destroyed')
        elif asteroid.size == 2 and asteroid.wasHidden:
            asteroids[asteroidIndex] = 'DESTROYED'
            asteroidLabels[asteroidIndex].hide()
            asteroidLabels[asteroidIndex] = 'DESTROYED'
            print('Medium asteroid has been destroyed')
        elif asteroid.size == 3 and asteroid.points != 300 and asteroid.wasHidden:
            asteroids[asteroidIndex] = 'DESTROYED'
            asteroidLabels[asteroidIndex].hide()
            asteroidLabels[asteroidIndex] = 'DESTROYED'

        elif asteroid.size == 3 and asteroid.points != 300 and asteroid.wasHidden == False:
            if asteroids[asteroidIndex - 2] != 'DESTROYED':
                asteroids[asteroidIndex - 2].isHidden = False
                asteroids[asteroidIndex - 2].posX = asteroid.posX
                asteroids[asteroidIndex - 2].posY = asteroid.posY
            if asteroids[asteroidIndex - 1] != 'DESTROYED':
                asteroids[asteroidIndex - 1].isHidden = False
                asteroids[asteroidIndex - 1].posX = asteroid.posX
                asteroids[asteroidIndex - 1].posY = asteroid.posY

            asteroids[asteroidIndex] = 'DESTROYED'
            asteroidLabels[asteroidIndex].hide()
            asteroidLabels[asteroidIndex] = 'DESTROYED'

            print('Big asteroid has been destroyed')
        elif asteroid.size == 3 and asteroid.points == 300:
            asteroids[asteroidIndex] = 'DESTROYED'
            asteroidLabels[asteroidIndex].hide()
            asteroidLabels[asteroidIndex] = 'DESTROYED'

            print('Gold asteroid has been destroyed')

    def createSmallAsteroid(self, x, y, direction, size):
        newAsteroid = Asteroid(size, x, y, 3, direction)

        lab = QLabel(self)
        if size == 1:
            newAsteroid.whatSizeAmI = 'SMALL';
            lab.setPixmap(self.smallAsteroidPixMap)
        else:
            newAsteroid.whatSizeAmI = 'MEDIUM';
            lab.setPixmap(self.mediumAsteroidPixMap)
        lab.setGeometry(x, y, 100, 100)
        asteroids.append(newAsteroid)
        asteroidLabels.append(lab)
        self.showAsteroids()

    def aliveAsteroidsCount(self):
        count = 0
        for a in asteroids:
            if a != 'DESTROYED':
                if not a.isHidden:
                    count += 1
        return count

    def destoryRandomAsteroid(self):
        asteroid = ''
        while True:
            randomAsteroidIndex = randint(0, len(asteroids) - 1)
            asteroid = asteroids[randomAsteroidIndex]
            if asteroid != 'DESTROYED':
                self.destroyAsteroid(asteroid)
                break

if __name__ == "__main__":
    app = QApplication(sys.argv);
    mainWindow = theMainWindow();
    sys.exit(app.exec_())
