import tensorflow as tf
import numpy as np
import math

def batch_norm(x, scope=''):
    from tensorflow.contrib.layers import batch_norm as layers_batch_norm
    batch_norm_epsilon = 1e-5
    return layers_batch_norm(x, epsilon=batch_norm_epsilon)

def weight_variable(shape, name):
    # Delving deep into Rectifier
    # http://arxiv.org/pdf/1502.01852v1.pdf)
    # fan_in, _ = get_fans(shape)
    if shape:
        fan_in = float(shape[-2]) if len(shape) > 1 else float(shape[-1])
        fan_out = float(shape[-1])
    else:
        fan_in = 1.0
        fan_out = 1.0
    for dim in shape[:-2]:
        fan_in *= float(dim)
        fan_out *= float(dim)

    # assert stddev > 0.001, stddev

    factor = 2.0
    stddev = math.sqrt(1.3 * factor / fan_in)

    initialization = tf.truncated_normal(shape, stddev=stddev)

    return tf.Variable(initialization, name=name)

def bias_variable(shape, name):
    initial = tf.constant(0.01, shape=shape)
    var = tf.Variable(initial, name=name)
    return var

def conv11x11(x, filters, **kwds):
    return conv(x, 11, 11, filters, **kwds)

def conv1x1(x, filters, **kwds):
    return conv(x, 1, 1, filters, **kwds)


def conv5x5(x, filters, **kwds):
    return conv(x, 5, 5, filters, **kwds)


def conv3x3(x, filters, **kwds):
    return conv(x, 3, 3, filters, **kwds)


def conv1x3(x, filters, **kwds):
    return conv(x, 1, 3, filters, **kwds)


def conv3x1(x, filters, **kwds):
    return conv(x, 3, 1, filters, **kwds)


def conv1x7(x, filters, **kwds):
    return conv(x, 1, 7, filters, **kwds)


def conv7x1(x, filters, **kwds):
    return conv(x, 7, 1, filters, **kwds)


def conv(x, w, h, filters, stride=1, padding="SAME", activation="relu", norm = False):
    # channels = x.get_shape().as_list()[3]
    #
    # kernel_shape = [w, h, channels, filters]
    # //kernel = weight_variable(kernel_shape, "kernel")
    # kernel = tf.Variable()
    #
    # x = tf.nn.conv2d(x, kernel, strides=[1, stride, stride, 1], padding=padding)
    #
    # if norm:
    #     out = batch_norm(x)
    # else:
    #     b = bias_variable([filters], "bias")
    #     out = tf.nn.bias_add(x, b)
    #
    # if activation == "relu":
    #     return tf.nn.relu(out)
    # if activation == "tanh":
    #     return tf.nn.tanh(out)

    out = tf.contrib.layers.convolution2d(inputs=x, num_outputs=filters, kernel_size=[w, h],
                                          stride=stride, padding=padding,
                                          weights_initializer=tf.contrib.layers.xavier_initializer_conv2d(),
                                          biases_initializer=tf.contrib.layers.xavier_initializer(),
                                          trainable=True)
    if activation == "relu":
        out = tf.nn.relu(out)
    elif activation == "tanh":
        out = tf.nn.tanh(out)
    return out


def max_pool_2x2(x, stride=2, padding="SAME"):
    return tf.nn.max_pool(x, ksize=[1, 2, 2, 1],
                          strides=[1, stride, stride, 1], padding=padding)


def max_pool_3x3(x, stride=2, padding="SAME"):
    return tf.nn.max_pool(x, ksize=[1, 3, 3, 1],
                          strides=[1, stride, stride, 1],
                          padding=padding)

def fc0(x, shape):
    W = weight_variable(shape, "weight")
    b = bias_variable([shape[-1]], "bias")
    return tf.add(tf.matmul(x, W), b)

# def constant_initializer(shape, dtype, partition_info, value=0.01):
#     return tf.fill(shape, value)

# Mateusz: not sure how the is_training() method is supposed to work so I'm leaving this WIP. Certainly needs cleanup!
def fc(x, shape):
    bias_initializer = lambda shape, dtype, partition_info: tf.fill(shape, 0.01)
    #tf.constant(True, name='global_is_training')
    #print("is training ", tf.Print(is_training()))
    out = tf.contrib.layers.fully_connected(inputs=x, num_outputs=shape[-1],
                                        weights_initializer=tf.contrib.layers.xavier_initializer(),
                                        activation_fn=None,
                                        normalizer_fn=tf.contrib.layers.batch_norm,
                                        normalizer_params={ 'is_training': True }, # only temporary until is_training() is put in correctly
                                        #normalizer_params={ 'is_training': is_training() },
                                        #biases_initializer=bias_initializer,
                                        #biases_initializer=constant_initializer(),
                                        #biases_initializer=tf.contrib.layers.xavier_initializer(),
                                        trainable=True)
    return out

def is_training():
    #return True
    return tf.get_default_graph().get_tensor_by_name("global_is_training:0")
    # with tf.variable_scope('') as scope:
    #     scope.reuse_variables()
    #     return tf.get_variable("is_training",
    #                            initializer=lambda *args, **kwds: False, shape=[],
    #                            trainable=False,
    #                            dtype=tf.bool)
