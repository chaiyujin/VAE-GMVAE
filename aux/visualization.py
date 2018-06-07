from matplotlib import pyplot as plt
import matplotlib as mpl
from sklearn.manifold import TSNE
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import numpy as np
import tensorflow as tf
from tensorflow.contrib.tensorboard.plugins import projector
import os


def plot_images_gen(shape, images_gen, n_plots_axis=5, K=-1, model_name='VAE'):
    '''
    Plot generated images.
    '''
    f, axarr = plt.subplots(n_plots_axis, n_plots_axis)
    num_imgs = images_gen.shape[0]
    idx = np.linspace(0,num_imgs -1,n_plots_axis*n_plots_axis).astype(int)
    count = 0
    if(shape[3] > 1):
        for i in range(n_plots_axis):
            for j in range(n_plots_axis):
                axarr[i, j].imshow(images_gen[idx[count], :].reshape([shape[1], shape[2], shape[3]]), cmap='gray')
                axarr[i, j].axis('off')
                count+=1
    else:
        for i in range(n_plots_axis):
            for j in range(n_plots_axis):
                axarr[i, j].imshow(images_gen[idx[count], :].reshape([shape[1], shape[2]]), cmap='gray')
                axarr[i, j].axis('off')
                count+=1
    if(K<0):
        f.suptitle('Images Generated by ' + model_name)
    else:
        f.suptitle('Images Generated by ' + model_name + ' ' + str(K))
    return f

def plot_summary(shape, batch_xs, batch_test,reconstructions_train, reconstructions_test, n_plots_axis=5,title1='Training Images', title2='Test Images'):
    '''
    Plot input images and their reconstructions for train and test.
    '''
    f1, axarr1 = plt.subplots(n_plots_axis, 2)
    f2, axarr2 = plt.subplots(n_plots_axis, 2)


    if(shape[3] > 1):
        for i in range(n_plots_axis):
            axarr1[i, 0].imshow(batch_xs[i, :].reshape([shape[1], shape[2], shape[3]]), cmap='gray')

            axarr1[i, 1].imshow(reconstructions_train[i, :].reshape([shape[1], shape[2], shape[3]]), cmap='gray')

            axarr2[i, 0].imshow(batch_test[i, :].reshape([shape[1], shape[2], shape[3]]), cmap='gray')

            axarr2[i, 1].imshow(reconstructions_test[i, :].reshape([shape[1], shape[2], shape[3]]), cmap='gray')

    else:
        for i in range(n_plots_axis):
            axarr1[i, 0].imshow(batch_xs[i, :].reshape([shape[1], shape[2]]), cmap='gray')

            axarr1[i, 1].imshow(reconstructions_train[i, :].reshape([shape[1], shape[2]]), cmap='gray')

            axarr2[i, 0].imshow(batch_test[i, :].reshape([shape[1], shape[2]]), cmap='gray')

            axarr2[i, 1].imshow(reconstructions_test[i, :].reshape([shape[1], shape[2]]), cmap='gray')


    f1.suptitle(title1)
    f2.suptitle(title2)
    return f1, f2

def plot_recons(shape, batch_xs, reconstructions_train,  n_plots_axis=5, title = 'Test Images'):
    f2, axarr2 = plt.subplots(n_plots_axis, 2)

    if(shape[3] > 1):
        for i in range(n_plots_axis):
            axarr2[i, 0].imshow(batch_xs[i, :].reshape([shape[1], shape[2], shape[3]]), cmap='gray')

            axarr2[i, 1].imshow(reconstructions_train[i, :].reshape([shape[1], shape[2], shape[3]]), cmap='gray')

    else:
        for i in range(n_plots_axis):
            axarr2[i, 0].imshow(batch_xs[i, :].reshape([shape[1], shape[2]]), cmap='gray')

            axarr2[i, 1].imshow(reconstructions_train[i, :].reshape([shape[1], shape[2]]), cmap='gray')



    f2.suptitle(title)
    return f2

def toGrayScale(image):
    r, g, b = image[:,:,0], image[:,:,1], image[:,:,2]
    # gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
    gray = 0 * r + 0 * g + 0 * b
    return gray;

def batchToGray(batch):
    if(batch.shape[3]==1):
        return batch;

    grey = np.zeros((batch.shape[0], batch.shape[1], batch.shape[1]))
    for ind in range(batch.shape[0]):
        grey[ind, :] = toGrayScale(batch[ind])
    return grey


def plot_embeddings(batch, labels, z, LOG_DIR, shape = (28,28,1), invert=True):
    '''
    Plot embeddings in TensorBoard.
    '''
    if(len(batch.shape) == 2):
        batch = np.reshape(batch, (-1,) + shape)
    sess = tf.InteractiveSession()
    # Specify where you find the metadata
    path_for_mnist_sprites = os.path.join(LOG_DIR, 'mnistdigits.png')
    path_for_mnist_metadata = os.path.join(LOG_DIR, 'metadata.tsv')

    to_visualise = batchToGray(batch)
    to_visualise = np.reshape(batch,[-1, batch.shape[1], batch.shape[2]] )

    if(invert):
        to_visualise = invert_grayscale(to_visualise)

    sprite_image = create_sprite_image(to_visualise)

    plt.imsave(path_for_mnist_sprites, sprite_image, cmap='gray')

    embedding_var = tf.Variable(z, name='z_space')
    summary_writer = tf.summary.FileWriter(LOG_DIR)

    config = projector.ProjectorConfig()
    embedding = config.embeddings.add()
    embedding.tensor_name = embedding_var.name

    embedding.metadata_path = 'metadata.tsv'  # 'metadata.tsv'

    # Specify where you find the sprite (we will create this later)

    embedding.sprite.image_path = 'mnistdigits.png'  # 'mnistdigits.png'

    img_w = batch.shape[2]
    embedding.sprite.single_image_dim.extend([img_w, img_w])

    # Say that you want to visualise the embeddings
    projector.visualize_embeddings(summary_writer, config)

    sess.run(tf.global_variables_initializer())
    saver = tf.train.Saver()
    saver.save(sess, os.path.join(LOG_DIR, "model.ckpt"), 1)
    with open(path_for_mnist_metadata, 'w') as f:
        f.write("Index\tLabel\n")
        for ind in range(0, len(z)):
            f.write("%d\t%d\n" % (ind,labels[ind]))

    return


def create_sprite_image(images):
    '''
    Returns a sprite image consisting of images passed as argument. Images should be count x width x height
    '''
    if isinstance(images, list):
        images = np.array(images)
    img_h = images.shape[1]
    img_w = images.shape[2]
    n_plots = int(np.ceil(np.sqrt(images.shape[0])))

    spriteimage = np.ones((img_h * n_plots, img_w * n_plots))

    for i in range(n_plots):
        for j in range(n_plots):
            this_filter = i * n_plots + j
            if this_filter < images.shape[0]:
                this_img = images[this_filter]
                spriteimage[i * img_h:(i + 1) * img_h, j * img_w:(j + 1) * img_w] = this_img

    return spriteimage


def vector_to_matrix_mnist(mnist_digits):
    '''
    Reshapes normal mnist digit (batch,28*28) to matrix (batch,28,28)
    '''
    return np.reshape(mnist_digits, (-1, 28, 28))


def invert_grayscale(mnist_digits):
    '''
    Makes black white, and white black
    '''
    return 1 - mnist_digits

def scatter_z_dim(latent, labels, perplexity=10, title="Scatter z dim"):

    f, axarr = plt.subplots(1, 1)
    latent_dim = latent.shape[1]

    colors = {0:'black', 1:'grey', 2:'blue', 3:'cyan', 4:'lime', 5:'green', 6:'yellow', 7:'gold', 8:'red', 9:'maroon'}
    if(latent_dim>2):
        tsne = TSNE(perplexity=perplexity, n_components=2, init='pca', n_iter=1000)
        latent_samples = tsne.fit_transform(latent)
    else:
        latent_samples = np.asarray(latent)


    for number, color in colors.items():
        axarr.scatter(x=latent_samples[labels==number, 0], y=latent_samples[labels==number, 1], color=color, label=str(number))


    axarr.legend()
    axarr.grid()
    f.suptitle(title, fontsize=20)
    return f



def plot_z_dim(latent_dim, recons_images, latent, perplexity=10, title="Plot z dim"):

    f, axarr = plt.subplots(1, 1, figsize=(8,8))

    if(latent_dim>2):
        tsne = TSNE(perplexity=perplexity, n_components=2, init='pca', n_iter=1000)
        latent_samples = tsne.fit_transform(latent)
    else:
        latent_samples = np.asarray(latent)

    axarr.clear()
    for i in range(0, len(latent)):
        im = OffsetImage(recons_images[i].reshape([28, 20]), zoom=1,cmap='gray')
        ab = AnnotationBbox(im, latent_samples[i], frameon=False)
        axarr.add_artist(ab)

    f.suptitle(title, fontsize=20)
    return f
